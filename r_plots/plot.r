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
nplots <- 4
log <- "y" # "", "y"
yat_log_must_include <- c(0:10, seq(20, 100, b=10), seq(200, 1000, b=100), 
                          seq(2000, 10000, b=1000), seq(20000, 100000, b=10000))
lm_obs_col <- "blue"
lm_predict_ntime <- 14
lm_predict_interval <- "day"
lm_predict_col <- "red"

for (ploti in seq_len(nplots)) {
    lm_from <- lm_to <- "" # default
    if (ploti == 1) {
        x <- ts$time
        y <- ts$confirmed
        ylab <- "confirmed per day"
        lm_from <- as.POSIXlt("2020-02-25", tz="UTC")
    } else if (ploti == 2) {
        x <- ts$time
        y <- cumsum(ts$confirmed)
        ylab <- "confirmed cumulative"
        lm_from <- as.POSIXlt("2020-03-02", tz="UTC")
    } else if (ploti == 3) {
        x <- ts$time[2:length(ts$time)]
        y <- diff(ts$confirmed)
        ylab <- "change of confirmed per day"
        lm_from <- as.POSIXlt("2020-02-25", tz="UTC")
    } else if (ploti == 4) {
        x <- ts$time
        y <- ts$deaths
        ylab <- "deaths"
    }
   
    # exponential model of obs
    if (!is.character(lm_from)) { # lm only from
        if (lm_from %in% x) {
            lm_from_ind <- which.min(abs(lm_from - x))
        } else {
            message("lm_from = ", lm_from, " is given but in range of x = ", min(x), " to ", max(x))
        }
    } else {
        lm_from_ind <- 1
    }
    if (!is.character(lm_to)) { # lm only to
        if (lm_to %in% x) {
            lm_to_ind <- which.min(abs(lm_to - x))
        } else {
            message("lm_to = ", lm_to, " is given but in range of x = ", min(x), " to ", max(x))
        }
    } else {
        lm_to_ind <- length(x)
    }
    lm_inds <- lm_from_ind:lm_to_ind
    #lm_inds <- seq_along(x)
    x_lm <- as.numeric(x)[lm_inds] # posix cannot be input for lm
    y_lm <- y[lm_inds] # numeric 0 cannot be input for lm
    x_lm[which(y_lm == 0)] <- NA 
    y_lm[which(y_lm == 0)] <- NA
    if (T) { # var = exp(time) <=> log(var) = time
        lm_log <- lm(log(y_lm) ~ x_lm) # if data is exponential: take log of data and fit against linear time
        x_lm_log_obs <- lm_log$model[,2]
        y_lm_log_obs <- exp(lm_log$fitted.values)
    } else if (F) { # exp(var) = exp(time) <=> log(var) = log(time)
        lm_log <- lm(log(y_lm) ~ log(x_lm))
        x_lm_log_obs <- exp(lm_log$model[,2])
        y_lm_log_obs <- exp(lm_log$fitted.values)
    }
    #nls_log <- nls(log(y_lm) ~ x_lm)

    # exponential model summary
    lm_log_summary <- summary(lm_log)
    dt <- unique(diff(x_lm))
    if (any(is.na(dt))) dt <- dt[-which(is.na(dt))]
    if (length(dt) != 1)  stop("dont know time factor for exponential model estimate")
    lm_log_estimate <- lm_log_summary$coefficients[2,1]*dt
    lm_log_uncert <- lm_log_summary$coefficients[2,2]*dt
    rsq <- lm_log_summary$r.squared
    pvalue <- lm_log_summary$coefficients[2,4]
    message("exponential model estimate = ", lm_log_estimate, " +- ", lm_log_uncert, "; r^2 = ", rsq, "; p = ", pvalue) 
    
    # exponential prediction
    x_lm_log_future <- seq.POSIXt(x[length(x)], l=lm_predict_ntime, b=lm_predict_interval)
    x_lm_log_future <- x_lm_log_future[-1] # remove last day of obs
    x_lm_log_future <- as.POSIXlt(x_lm_log_future)
    x_lm_log_future_lm <- as.numeric(x_lm_log_future) # input for predict 
    x_lm_log_future_lm <- data.frame(x_lm=x_lm_log_future_lm) 
    lm_log_future <- predict(lm_log, newdata=x_lm_log_future_lm, interval="prediction")
    y_lm_log_future <- exp(lm_log_future)

    # prepare plot
    ts_tlimlt <- range(x, x_lm_log_future)
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
    if (log == "y") y[which(y == 0)] <- NA
    ylim <- range(y, y_lm_log_obs, y_lm_log_future, na.rm=T)
    ylim[2] <- ylim[2] + 0.05*diff(ylim)
    yat <- pretty(ylim, n=30)
    if (log == "y") {
        yat <- sort(unique(c(yat, yat_log_must_include)))
    }

    # plot
    plotname <- paste0("plots/", country, "_", gsub(" ", "_", ylab), 
                       ifelse(log != "", paste0("_log", log), ""), 
                       ".png")
    message("plot ", plotname)
    png(plotname, width=3000, height=1666, res=300)
    par(mar=c(5.1, 6.1, 4.1, 6.1) + 0.1)
    plot(x, y, xaxt="n", yaxt="n", t="n",
         log=log,
         xlab="date", ylab=NA,
         xlim=ts_tlimn, ylim=ylim)
    message("ylim = ", appendLF=F)
    dput(ylim)
    message("par(\"usr\") = ", appendLF=F)
    dput(par("usr"))
    axis(1, at=ts_tatn, labels=rep("", t=length(ts_tatn)))
    text(x=ts_tatn, y=grconvertY(-0.08, from="npc"), labels=ts_tlablt, xpd=T, srt=90, cex=0.5)
    axis(2, at=yat, las=2, cex.axis=0.5)
    mtext(side=2, text=ylab, line=3)
    axis(4, at=yat, las=2, cex.axis=0.5)
    mtext(side=4, text=ylab, line=3)

    # add grid
    abline(h=yat, col="gray", lwd=0.5)
    abline(v=ts_tatn, col="gray", lwd=0.5)
   
    # add title
    title(paste0(ylab, " in ", country, " at ", max(x)), cex.main=0.85)

    # add obs
    points(x, y, t="o")
    
    if (F) { # add day of month of obs
        text(x, y, labels=x$mday, pos=3, cex=0.5) # pos=3: above; todo: pos destroys center adjustment

    } else if (T) { # add value of obs
        text(x, y, labels=y, pos=3, cex=0.5, srt=90) # pos=3: above; todo: pos destroys center adjustment
    }

    # add exponential model of obs
    points(x_lm_log_obs, y_lm_log_obs, t="o", col=lm_obs_col)

    # add uncertainty of exponential model of future
    polygon(c(x_lm_log_future, rev(x_lm_log_future)),
            c(y_lm_log_future[,"lwr"], rev(y_lm_log_future[,"upr"])),
            col=rgb(t(col2rgb(lm_predict_col)/255), alpha=0.2), border=NA)

    # add exponential model of future
    points(x_lm_log_future, y_lm_log_future[,"fit"], t="o", col=lm_predict_col)

    if (F) { # add day of month of prediction
        text(x_lm_log_future, y_lm_log_future[,"fit"], labels=x_lm_log_future$mday, pos=3, cex=0.5) # pos=3: above
    } else if (T) { # add value of prediction
        text(x_lm_log_future, y_lm_log_future[,"fit"], labels=round(y_lm_log_future[,"fit"]), 
             pos=3, cex=0.5, srt=90) # pos=3: above
    }

    # legend
    lm_text <- c("obs",
                 eval(substitute(expression(paste("exponential model = exp[ (", estimate, "" %+-% "", uncert, 
                                                  ") " %*% " time ]; r = ", rsq, "; p ", p)),
                                 list(estimate=round(lm_log_estimate, 2), uncert=round(lm_log_uncert, 2),
                                      rsq=round(sqrt(rsq), 2), p=ifelse(pvalue < 1e-5, "<= 1e-5", paste0("= ", pvalue))))),
                 eval(substitute(expression(paste("exponential prediction (doubling time = ", estimate, ""^paste(-1), " = ", 
                                                  doubling_time, " days)")),
                                 list(estimate=round(lm_log_estimate, 2), doubling_time=round(dt/(lm_log_estimate*dt), 2)))))
    legend("topleft", legend=lm_text,
           col=c("black", lm_obs_col, lm_predict_col),
           lty=1, lwd=1, pch=1, 
           bty="n", x.intersp=0.2)

    # save plot
    dev.off()

} # ploti


