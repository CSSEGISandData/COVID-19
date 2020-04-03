
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#
library(shiny)
library(plotly)
library(shinyjs)

shinyUI(fluidPage(
  
  #Use shinyjs to allow for advanced UI functionality
  useShinyjs(),

  # Application title
  titlePanel("COVID-19 Case Plotter"),
  
  tabsetPanel(  
  tabPanel("Dynamic Plots",
           
           textOutput('test_text'),
          
           h3("Select Provinces/States/Countries"),
           
           # Dropdown selector to select from country, province, or custom search
           fluidRow(
           column(4, selectInput('subregion_type', label = 'Select by...', choices = c("Province", "Country", "Text String"), selected = "Country")),
           column(4, uiOutput("ui_province_region_dropdown")),
           column(4, textInput(inputId = "region_search_text", label = 'Enter text to match region names. Multiple entries should be separated by a semicolon and space.', value = "", placeholder = 'Enter text to search by partial string matching'))),
           
           hr(),
           
           h3("Selected region(s)"),
           textOutput('selected_areas'),
           
           hr(),
           fluidRow(
             column(3, checkboxInput('y_log_scale_data', label = 'Apply log scaling to y-axis', value = FALSE)),
             column(3, checkboxInput('simulate_recovery_data', label = 'Simulate resolution data', value = FALSE)),
             column(3, selectInput('simulation_dist', label = 'Distribution to simulate recovery time', choices = c("Lognormal", "Exponential", "Poisson", "Weibull", "Negative Binomial"), selected = "Lognormal")),
             column(3, numericInput('mean_recovery_days', label = 'Mean time to recovery for simulation', value = 21)),
           ),
           
           h3("Plot of new cases for the selected region(s)."),
           plotlyOutput("obs_data_plot"),
           
           
           fluidRow(
             column(3, sliderInput('predict_days', label = 'Days to predict ahead', min = 0, max = 14, step = 1, value = 0)),
             column(3, uiOutput("model_date_selector")),
             column(3, checkboxInput('y_log_scale_model', label = 'Apply log scaling to y-axis', value = TRUE)),
             column(3, uiOutput("series_selector")),
           ),
           h3('Exponential growth model for selected dataset'),
           h4('A partitioned tree exponential growth over time model is shown fitted to this data. Each segment is a simple exponential growth model.'),
           plotlyOutput("log_plot_cases"),
           
           hr(),
           h3("Estimated doubling time (in days) for each model slope above (from left to right)."),
           tableOutput('doubling_time_table')
             
  )
  )
))
