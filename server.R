
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(nlme)
library(partykit)
library(corrplot)
library(plotly)
library(shinyjs)

# Ingest daily report data from John's Hopkins daily reports and translate to cumulative data by day
cumulative_data = ingest_daily_to_time_series(directory = 'csse_covid_19_data/csse_covid_19_daily_reports')

test_time = Sys.time()

shinyServer(function(input, output) {
  
  
  ########################################################################################
  
  ##################INPUT GENERATORS
  
  ########################################################################################
  
  #Generate a drop-down selector for each province name
  output$ui_province_region_dropdown <- renderUI({
    if(input$subregion_type == 'Province'){
      choice_vec = unique(cumulative_data$Confirmed$Province.State)
    }else if(input$subregion_type == 'Country'){
      choice_vec = unique(cumulative_data$Confirmed$Country.Region)
    }else{
      choice_vec = c('Use text search on right')
    }
    selectInput(inputId = 'subset_names', label = 'Select one or more region(s) to plot', choices = choice_vec, multiple = TRUE)
  })
  
  # Generate drop-down selector for data series to model using log-modeler
  output$series_selector <- renderUI({
    
    summarized_series = summarize_subsets()
    
    choice_vec = c()
    
    if(!is.null(summarized_series)){
      
      choice_vec = names(summarized_series)
      selected = choice_vec[1]
    }
    selectInput(inputId = 'log_model_series_selector', label = 'Plot Series', choices = choice_vec, selected=selected)
  })
  
  
  # Generate date range selector for data series to model using log-modeler
  output$model_date_selector <- renderUI({
    
    summarized_series = summarize_subsets()
    first_case_date = min(summarized_series[[1]]$formatted_dates)
    last_data_date = max(summarized_series[[1]]$formatted_dates)
    
    dateRangeInput(inputId = 'model_date_range', label = 'Select dates to use for model',
                   start = first_case_date, min = first_case_date, end = last_data_date, max = last_data_date)
  })
  
  
  ########################################################################################
  
  ################## CORE CALCULATIONS
  
  ########################################################################################  
  

  summarize_subsets <- reactive({
    
    # Prepare arguments for function call to summarize subset
    provinces = c()
    countries = c()
    text_string = ''
    
    if(input$subregion_type == 'Province'){
      
      provinces = input$subset_names
      
    }
    
    if(input$subregion_type == 'Country'){
      
      countries = input$subset_names
      
    }
    
    if(input$subregion_type == 'Text String'){
      
      text_string = input$region_search_text
      
    }
    
    
    # Iterate through each dataset to summarize it for the selected region(s)
    summarized_data = list()
    
    # Get confirmed case data
    summarized_data[[length(summarized_data) + 1]] = summarize_dataset(cumulative_data$Confirmed, provinces, countries, text_string, count_columns = cumulative_data$DateColumns)
    
    # Get recovered case data
    summarized_data[[length(summarized_data) + 1]] = summarize_dataset(cumulative_data$Recovered, provinces, countries, text_string, count_columns = cumulative_data$DateColumns)
    
    # Get death case data
    summarized_data[[length(summarized_data) + 1]] = summarize_dataset(cumulative_data$Deaths, provinces, countries, text_string, count_columns = cumulative_data$DateColumns)
    
    # Get death plus recovered data
    death_recovered_dataset = cumulative_data$Recovered
    count_columns = cumulative_data$DateColumns
    death_recovered_dataset[, count_columns] = cumulative_data$Recovered[, count_columns] + cumulative_data$Deaths[, count_columns]
    summarized_data[[length(summarized_data) + 1]] = summarize_dataset(death_recovered_dataset, provinces, countries, text_string, count_columns = cumulative_data$DateColumns)
    
    # Get active case data
    active_dataset = cumulative_data$Confirmed
    count_columns = cumulative_data$DateColumns
    active_dataset[, count_columns] = cumulative_data$Confirmed[, count_columns] - cumulative_data$Recovered[, count_columns] - cumulative_data$Deaths[, count_columns]
    summarized_data[[length(summarized_data) + 1]] = summarize_dataset(active_dataset, provinces, countries, text_string, count_columns = cumulative_data$DateColumns)
    
    # Name each entry in summarized_data list
    names(summarized_data) = c('Confirmed', 'Recovered', 'Deaths', 'Deaths + Recovered', 'Active')
    
    return(summarized_data)
    
  })
  
  
  log_modeler <- reactive({
    
    selected_dat = summarize_subsets()[[input$log_model_series_selector]]
    plot_dat = selected_dat$case_counts
    
    # Restrict data per selected date range
    valid_values = selected_dat$formatted_dates >= input$model_date_range[1] & selected_dat$formatted_dates <= input$model_date_range[2]
    
    # Additionally restrict data to values > 0
    valid_values = valid_values & plot_dat > 0
    
    # Convert to vector of selected positions
    valid_values = which(valid_values)
    
    
    X = valid_values
    Y = plot_dat[valid_values]
    
    # Fit partition tree with linear regression model in each leaf with splitting controlled by statistical significance
    mod = lmtree(log(Y) ~ X | X)
    
    # Get 95% confidence intervals over fitted window
    fitted_values = predict(mod, newdata = data.frame(X, Y), interval = 'confidence')
    fitted_values = exp(fitted_values)
    
    # Create prediction interval for requested number of days ahead
    predictions = NULL
    if(input$predict_days > 0){
      
      # Generate predictions with prediction interval for requested number of days ahead
      predictions = predict(mod, newdata = data.frame(X = c(0:input$predict_days) + max(X)), interval = 'prediction')
      predictions = exp(predictions)
      
    }
    
    return(list('date_names' = names(Y),
                'X' = X,
                'Y' = Y,
                'model' = mod,
                'fitted_values' = fitted_values,
                'predictions' = predictions))
    
  })
  
  ########################################################################################
  
  ################## OUTPUTS
  
  ########################################################################################
  
  output$selected_areas <- renderText({
    
    region_text = summarize_subsets()[['Confirmed']][['selected_regions']]
    region_text = paste0(region_text, sep = ';  ')
    return(region_text)
    
  })
  
  output$obs_data_plot <- renderPlotly({
    
    raw_data = summarize_subsets()
    
    if(is.null(raw_data$Confirmed$selected_regions)){
      
      return('Select a country/province to plot data')
      
    }else{
      
      # Create figure format
      fig <- plot_ly(type = 'scatter', mode = 'none')
      
      # Loop through all entries in raw_data list and add them to the plot
      for(i in 1:length(raw_data)){
        fig <- fig %>% add_trace(x = raw_data[[i]]$formatted_dates, y = raw_data[[i]]$case_counts, name = names(raw_data)[i], fill = 'tozeroy')
      }
      
      # If recovery data should be simulated, add it
      if(input$simulate_recovery_data){
        
        # Create the argument list shell for the resolution_simulation function with data arguments
        argument_list = list('cumulative_confirmed_vec' = raw_data$Confirmed$case_counts,
                             'end_point' = length(raw_data$Confirmed$case_counts))
        
        # Fix any errors in the cumulative case count (decrease from one day to next, which is impossible)
        for (i in 2:length(argument_list$cumulative_confirmed_vec)){
          
          # If the current day cumulative count is less than the previous day, correct the error by setting it equal to the previous day's count
          if(argument_list$cumulative_confirmed_vec[i] < argument_list$cumulative_confirmed_vec[i-1]){
            
            argument_list$cumulative_confirmed_vec[i] = argument_list$cumulative_confirmed_vec[i-1]
            
          }
          
        }
        
        # Find the best fit for the selected distribution
        distribution_fit = resolution_dist_fit(cumulative_confirmed_vec = raw_data$Confirmed$case_counts,
                                               cumulative_resolved_vec =raw_data$'Deaths + Recovered'$case_counts,
                                               distribution = input$simulation_dist)
        print(distribution_fit)
        
        if(input$simulation_dist == 'Lognormal'){
          
          # argument_list = append(argument_list, list('distribution_func' = rlnorm,
          #                      'meanlog' = log(input$mean_recovery_days), 'sdlog' = 1))
          argument_list = append(argument_list, list('distribution_func' = rlnorm,
                                                     # 'distribution_cdf_func' = plnorm,
                                                     'meanlog' = distribution_fit$par[1], 'sdlog' = distribution_fit$par[2]))
        }else if(input$simulation_dist == 'Exponential'){
          
          # argument_list = append(argument_list, list('distribution_func' = rexp, 'rate' = 1 / input$mean_recovery_days))
          argument_list = append(argument_list, list('distribution_func' = rexp,
                                                     # 'distribution_cdf_func' = pexp,
                                                     'rate' = distribution_fit$par[1]))
          
        }else if(input$simulation_dist == 'Poisson'){
          
          argument_list = append(argument_list, list('distribution_func' = rpois,
                                                     # 'distribution_cdf_func' = ppois,
                                                     'lambda' = distribution_fit$par[1]))
        }else if(input$simulation_dist == 'Weibull'){
          
          argument_list = append(argument_list, list('distribution_func' = rweibull,
                                                     # 'distribution_cdf_func' = rweibull,
                                                     'shape' = distribution_fit$par[1], 'scale' = distribution_fit$par[2]))
        }else if(input$simulation_dist == 'Negative Binomial'){
          
          argument_list = append(argument_list, list('distribution_func' = rnbinom,
                                                     # 'distribution_cdf_func' = rnbinom,
                                                     'size' = distribution_fit$par[1], 'mu' = distribution_fit$par[2]))
        }
        
        # Simulate the resolution data with the specified distribution and arguments
        resolution_vec = do.call(resolution_simulation, argument_list)
        
        fig <- fig %>% add_trace(x = raw_data$Confirmed$formatted_dates, y = resolution_vec, name = 'Simulated Resolution', mode = 'lines', line = list(dash = 'dash'))
        fig <- fig %>% add_trace(x = raw_data$Confirmed$formatted_dates, y = argument_list$cumulative_confirmed_vec - resolution_vec, name = 'Simulated Active', mode = 'lines', line = list(dash = 'dot'))
        
      }
      
      if(input$y_log_scale_data){
        
        y_axis_format_list = list(title = 'Cases', type = "log")
      }else{
        y_axis_format_list = list(title = 'Cases')
      }
      
      fig <- layout(fig, yaxis = y_axis_format_list,
                    xaxis = list(title = 'Date'))
      
    }
  })
  
  output$log_plot_cases <- renderPlotly({
    
    selected_dat = summarize_subsets()[[input$log_model_series_selector]]
    
    model_data = log_modeler()
    
    if(is.null(model_data$fitted_values)){
      
      return('Select a country/province to plot data')
      
    }else{
      
      plot_df = data.frame(model_data$fitted_values)
      plot_df$X = c(model_data$X)
      plot_df$Y = c(model_data$Y)
      plot_df$date = as.Date(model_data$date_names, format = "%m-%d-%y")
      
      # Initialize plot
      fig <- plot_ly(plot_df, x = ~date)
      
      # Add raw data of entire series (it can be filtered in the javascript)
      fig <- fig %>% add_trace(y = selected_dat$case_counts, x = selected_dat$formatted_dates, name = 'raw data', mode = 'markers', marker = list(color = 'red'))
      
      # Add model traces
      fig <- fig %>% add_trace(y = ~fit, name = 'model_fit',mode = 'lines', line = list(color = 'blue'))
      fig <- fig %>% add_trace(y = ~lwr, name = 'lower_CI',mode = 'lines', fill='tonexty', fillcolor='rgba(168, 216, 234, 0.5)', line = list(width = 0))
      fig <- fig %>% add_trace(y = ~upr, name = 'upper_CI',mode = 'lines', fill='tonexty', fillcolor='rgba(168, 216, 234, 0.5)', line = list(width = 0))
      
      # Add predictions if they are requested
      if (!is.null(model_data$predictions)){
        
        pred_df = data.frame(model_data$predictions)
        pred_df$date = plot_df$date[nrow(plot_df)] + c(0:(nrow(pred_df)-1))
        
        
        fig <- fig %>% add_trace(data = pred_df, x = ~date, y = ~fit, name = 'pred_future',mode = 'lines')
        fig <- fig %>% add_trace(data = pred_df, x = ~date, y = ~lwr, name = 'lower_CI',mode = 'lines', fill='tonexty', fillcolor='rgba(234, 168, 216, 0.5)', line = list(width = 0))
        fig <- fig %>% add_trace(data = pred_df, x = ~date, y = ~upr, name = 'upper_CI',mode = 'lines', fill='tonexty', fillcolor='rgba(234, 168, 216, 0.5)', line = list(width = 0))
        
      }
      
      if(input$y_log_scale_model){
        
        y_axis_format_list = list(title = 'Cumulative Confirmed Cases', type = "log")
      }else{
        y_axis_format_list = list(title = 'Cumulative Confirmed Cases')
      }
      
      fig <- layout(fig, yaxis = y_axis_format_list,
                    xaxis = list(title = 'Date'))
      
    }
  })
  
  output$doubling_time_table <- renderTable({
    
    
    log_model = log_modeler()[['model']]
    
    # Initialize data frame
    result_table = data.frame('Segment' = c(1:(length(nodeids(log_model, terminal = TRUE)))))
    result_table$Est.Doubling.Time = NA
    result_table$Low.95.CI = NA
    result_table$High.95.CI = NA
    
    # Get coefficients and confidence interval for each fitted linear model in partition tree
    coef_list = partykit:::apply_to_models(log_model, node = nodeids(log_model, terminal = TRUE), FUN = coef)
    confint_list = partykit:::apply_to_models(log_model, node = nodeids(log_model, terminal = TRUE), FUN = confint)
    
    # Enter into appropriate segment in table
    for(i in 1:length(coef_list)){
      result_table$Est.Doubling.Time[i] = coef_list[[i]]['X']
      result_table[i, c('High.95.CI', 'Low.95.CI')] = confint_list[[i]]['X',]
    }
    
    result_table[,c('Est.Doubling.Time', 'Low.95.CI', 'High.95.CI')] = log(2) / result_table[,c('Est.Doubling.Time', 'Low.95.CI', 'High.95.CI')]
    
    return(result_table)
    
  })
  
  output$test_text <- renderText({

    return(paste('Data last synchoronized with Johns Hopkins:', format(test_time, "%H:%M %m-%d-%y"), collapse = ' '))
    
  })
  
})