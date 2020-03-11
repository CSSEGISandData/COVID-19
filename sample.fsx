#load @".paket\load\netcoreapp3.1\main.group.fsx"

open XPlot.Plotly
open FSharp.Data
open System

fsi.AddPrinter<DateTime>(fun dt -> dt.ToShortDateString())


[<Literal>]
let FilePath = __SOURCE_DIRECTORY__ + @"/csse_covid_19_data/csse_covid_19_daily_reports/01-22-2020.csv"
type Daily = CsvProvider<FilePath>

let files =
    System.IO.Directory.GetFiles("csse_covid_19_data/csse_covid_19_daily_reports", "*.csv")
    |> Seq.map System.IO.Path.GetFullPath

let makeScatter (country, values) =
    let dates, values = values |> Seq.toArray |> Array.unzip
    let t = Scatter(x = dates, y = values) :> Trace
    t.name <- country
    t

let allData =
    files
    |> Seq.map Daily.Load
    |> Seq.collect(fun data -> data.Rows)

let cleanedData =
    allData
    |> Seq.map (fun row ->
        row.``Country/Region``.Trim(),
        row.``Last Update``.Date,
        row.Confirmed.GetValueOrDefault 0)
    |> Seq.filter (fun (country,_,_) -> country <> "Others")

let byCountry =
    cleanedData
    |> Seq.groupBy (fun (country,date,_) -> country, date)
    |> Seq.map (fun (group, rows) ->
        group, rows |> Seq.sumBy (fun (_,_,confirmed) -> confirmed))
    |> Seq.groupBy (fun ((country,_), _) -> country)
    |> Seq.map (fun (country, rows) ->
         country, rows |> Seq.map (fun ((_, date), confirmed) -> date, confirmed))

let topTen =
    byCountry
    |> Seq.sortByDescending(fun (_, rows) ->
        let (_, confirmed) = rows |> Seq.last
        confirmed)
    |> Seq.skip 1
    |> Seq.take 10

topTen
|> Seq.map makeScatter
|> Chart.Plot
|> Chart.Show

