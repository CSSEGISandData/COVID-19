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

let byCountry =
    allData
    |> Seq.filter(fun row -> row.``Country/Region`` <> "Others")
    |> Seq.groupBy(fun a -> a.``Country/Region``, a.``Last Update``.Date)
    |> Seq.map(fun (key, rows) ->
        key, rows |> Seq.sumBy(fun row -> row.Confirmed.GetValueOrDefault 0))
    |> Seq.groupBy(fun (key, _) -> fst key)
    |> Seq.map(fun (country, rows) ->
        country.Trim(), rows |> Seq.map(fun ((_, date), confirmed) -> date, confirmed))

let topTen =
    byCountry
    |> Seq.sortByDescending(fun (_, rows) ->
        let _, confirmed = rows |> Seq.last
        confirmed)
    |> Seq.skip 1
    |> Seq.take 10

topTen
|> Seq.map makeScatter
|> Chart.Plot
|> Chart.Show

