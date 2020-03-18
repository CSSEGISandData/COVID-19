# r

rm(list=ls()); graphics.off()

## which country
country <- "Germany"


## read time series
message("\nread \"", country, "\" time series ...")
fconfirmed <- "../csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
fdeaths <- "../csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
frecovered <- "../csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

ts_confirmed <- read.csv(fconfirmed, header=T, stringsAsFactors=F, na.strings="")
ts_deaths <- read.csv(fdeaths, header=T, stringsAsFactors=F, na.strings="")
ts_recovered <- read.csv(frecovered, header=T, stringsAsFactors=F, na.strings="")

country_ts_ind <- which(ts_confirmed$Country.Region == country)
if (length(country_ts_ind) == 0) {
    stop("could not find country \"", country, "\"")
} else if (length(country_ts_ind) > 1) {
    stop("found several \"", country, "\" countries: \"", 
         paste(ts_confirmed$Country.Region[country_ts_ind], collapse="\", \""), "\"")
}

ts_dates <- colnames(ts_confirmed)
ts_data_col_inds <- which(substr(ts_dates, 1, 1) == "X") # stupid
ts_dates <- ts_dates[ts_data_col_inds] # X1.22.20 = January 22, 2020
ts_dates <- substr(ts_dates, 2, nchar(ts_dates))
ts_dates <- as.Date(ts_dates, format="%m.%d.%y")

ts <- vector("list")
ts$time <- as.POSIXlt(ts_dates)
ts$confirmed <- unlist(ts_confirmed[country_ts_ind,ts_data_col_inds])
attr(ts$confirmed, "names") <- NULL
ts$deaths <- unlist(ts_deaths[country_ts_ind,ts_data_col_inds])
attr(ts$deaths, "names") <- NULL
ts$recovered <- unlist(ts_recovered[country_ts_ind,ts_data_col_inds])
attr(ts$recovered, "names") <- NULL
message(country, " ts:")
cat(capture.output(str(ts)), sep="\n")


## read daily reports
message("\nread \"", country, "\" reports ...")
report_path <- "../csse_covid_19_data/csse_covid_19_daily_reports"
report_files <- list.files(report_path, pattern=glob2rx("*.csv"))
report_dates <- confirmed <- deaths <- recovered <- rep(NA, t=length(report_files))
for (fi in seq_along(report_files)) {
    freport <- paste0(report_path, "/", report_files[fi]) # 01-22-2020.csv
    tmp <- read.csv(freport, header=T, stringsAsFactors=F, na.strings="")
    country_report_ind <- which(tmp$Country.Region == "Germany")
    if (length(country_report_ind) == 0) {
        message("could not find country \"", country, "\" in report \"", report_files[fi], "\"")
    } else if (length(country_report_ind) > 1) {
        message("found several \"", country, "\" countries: \"", 
                paste(tmp$Country.Region[country_report_ind], collapse="\", \""), 
                "\" in \"", report_files[fi], "\"")
    } else { # country found in report data
        #report_dates[fi] <- tmp[country_report_ind,"Last.Update"] # 2020-03-17T11:53:10
        # --> formats of "Last.Update" column not always the same
        # --> use date from file
        report_dates[fi] <- tools::file_path_sans_ext(report_files[fi])
        confirmed[fi] <- tmp[country_report_ind,"Confirmed"]
        deaths[fi] <- tmp[country_report_ind,"Deaths"]
        recovered[fi] <- tmp[country_report_ind,"Recovered"]
    }
} # for fi report_files
report_dates <- as.Date(report_dates, format="%m-%d-%y")
report_dates <- as.POSIXlt(report_dates)
report <- list(time=report_dates, confirmed=confirmed, 
               deaths=deaths, recovered=recovered)
message(country, " report:")
cat(capture.output(str(report)), sep="\n")


## plot ts
nplots <- 3
lm_obs_col <- "blue"
lm_predict_ntime <- 10
lm_predict_interval <- "day"
lm_predict_col <- "red"
for (ploti in seq_len(nplots)) {
    if (ploti == 1) {
        x <- ts$time
        y <- ts$confirmed
        ylab <- "confirmed"
    } else if (ploti == 2) {
        x <- ts$time[2:length(ts$time)]
        y <- diff(ts$confirmed)
        ylab <- "change of confirmed per day"
    } else if (ploti == 3) {
        x <- ts$time
        y <- ts$deaths
        ylab <- "deaths"
    }
    
    # exponential model
    x_future <- seq.POSIXt(x[length(x)], l=lm_predict_ntime, b=lm_predict_interval)
    x_future <- x_future[-1] # remove last day of obs
    x_future <- as.POSIXlt(x_future)
    x_lm <- as.numeric(x) # posix cannot be input for lm
    y_lm <- y # numeric 0 cannot be input for lm
    y_lm[which(y_lm == 0)] <- NA
    lm_log <- lm(log(y_lm) ~ x_lm)

    # exponential model prediction
    x_future_lm <- as.numeric(x_future)
    x_future_lm <- data.frame(x_lm=x_future_lm) # input for predict
    lm_log_future <- predict(lm_log, newdata=x_future_lm, interval="prediction")
    
    # prepare plot
    ts_tlimlt <- range(x, x_future)
    ts_tlimn <- as.numeric(ts_tlimlt)
    ts_tlablt <- as.POSIXlt(pretty(ts_tlimlt, n=length(x)))
    if (any(ts_tlablt < ts_tlimlt[1])) {
        ts_tlablt <- ts_tlablt[-which(ts_tlablt < ts_tlimlt[1])]
    }
    if (any(ts_tlablt > ts_tlimlt[2])) {
        ts_tlablt <- ts_tlablt[-which(ts_tlablt > ts_tlimlt[2])]
    }
    ts_tatn <- as.numeric(ts_tlablt)
    ts_tlablt <- paste0(month.abb[ts_tlablt$mon+1], " ", ts_tlablt$mday)
    ylim <- range(y, exp(lm_log$fitted.values), exp(lm_log_future[,"fit"]))
    yat <- pretty(ylim, n=30)
    ylim[2] <- ylim[2] + 0.05*diff(ylim)

    # plot
    png(paste0(gsub(" ", "_", ylab), ".png"), width=3000, height=1666, res=300)
    par(mar=c(5.1, 6.1, 4.1, 6.1) + 0.1)
    plot(x, y, xaxt="n", yaxt="n", t="n",
         xlab="date", ylab=NA,
         xlim=ts_tlimn, ylim=ylim)
    axis(1, at=ts_tatn, labels=rep("", t=length(ts_tatn)))
    text(x=ts_tatn, y=ylim[1] - 0.1*diff(ylim), labels=ts_tlablt, xpd=T, srt=90, adj=1, cex=0.5)
    axis(2, at=yat, las=2, cex.axis=0.5)
    mtext(side=2, text=ylab, line=3)
    axis(4, at=yat, las=2, cex.axis=0.5)
    mtext(side=4, text=ylab, line=3)
    
    # add grid
    abline(h=yat, col="gray", lwd=0.5)
   
    # add title
    title(paste0(country, " at ", max(x)))

    # add obs
    points(x, y, t="o")
    
    # add day of month of obs
    text(x, y, labels=x$mday, pos=3, cex=0.5) # pos=3: above

    # add exponential model of obs
    points(lm_log$model[,2], exp(lm_log$fitted.values), t="o", col=lm_obs_col)

    # add uncertainty of exponential model of future
    polygon(c(x_future, rev(x_future)),
            c(exp(lm_log_future[,"lwr"]), rev(exp(lm_log_future[,"upr"]))),
            col=rgb(t(col2rgb(lm_predict_col)/255), alpha=0.2), border=NA)

    # add exponential model of future
    points(x_future, exp(lm_log_future[,"fit"]), t="o", col=lm_predict_col)

    # add day of month of prediction
    text(x_future, exp(lm_log_future[,"fit"]), labels=x_future$mday, pos=3, cex=0.5) # pos=3: above
   
    # legend
    legend("topleft", 
           c("obs", "exponential model", "exponential prediction"),
           col=c("black", lm_obs_col, lm_predict_col),
           lty=1, lwd=1, pch=1, 
           bty="n", x.intersp=0.2)

    # save plot
    dev.off()

} # ploti


