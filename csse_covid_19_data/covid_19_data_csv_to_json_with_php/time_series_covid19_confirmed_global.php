
<?php

/* 
 * Created by Resul Rıza DOLANER on 2020-03-26.
 * Converts CSV to JSON for Time Series Covid19 Confirmed Global CSV File
 */

header('Content-type: application/json');

// Set your CSV feed
$feed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv";

$keys = array();
$newArray = array();

// Function to convert CSV into associative array
function csvToArray($file, $delimiter)
{
  if (($handle = fopen($file, 'r')) !== FALSE) {
    $i = 0;
    while (($lineArray = fgetcsv($handle, 4000, $delimiter, '"')) !== FALSE) {
      for ($j = 0; $j < count($lineArray); $j++) {
        $arr[$i][$j] = $lineArray[$j];
      }
      $i++;
    }
    fclose($handle);
  }
  return $arr;
}

$data = csvToArray($feed, ',');

// Set number of elements
$count = count($data) - 1;

//Use first row for names  
$labels = array_shift($data);

foreach ($labels as $label) {
  $keys[] = $label;
}

// Add Ids, just in case we want them later
$keys[] = 'id';

for ($i = 0; $i < $count; $i++) {
  $data[$i][] = $i;
}

// Bring it all together
for ($j = 0; $j < $count; $j++) {
  $d = array_combine($keys, $data[$j]);
  $newArray[$j] = $d;
}

// Out as JSON
$data = json_encode($newArray);

/*
 * Here we will group the cities of the countries and gather them under a single heading.
 */

// Group data by the "Country/Region" key 
$byGroup = group_by("Country/Region", $newArray);

/**
 * Function that groups an array of associative arrays by some key.
 * 
 * @param {String} $key Property to sort by.
 * @param {Array} $data Array that stores multiple associative arrays.
 */
function group_by($key, $data)
{
  $result = array();

  foreach ($data as $val) {
    if (array_key_exists($key, $val)) {
      $result[$val[$key]][] = $val;
    } else {
      $result["test"][] = $val;
    }
  }

  return $result;
}

// Grouped json result
echo json_encode($byGroup);

?>