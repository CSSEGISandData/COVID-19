
<?php

/* 
 * Created by Resul Rıza DOLANER on 2020-03-26.
 * Converts CSV to JSON for Covid19 Daily Reports CSV File
 */

header('Content-type: application/json');


/**
 * Data always contains data from the day before. 
 * That's why we set the date to get the last day data from each call. 
 * You can also edit for the day you want to shoot.
 */
$day = date("d");
$mounth = date("m");
$year = date("Y");
$getDateString = ($mounth) . "-" . ($day - 1) . "-" . $year;

// Set your CSV feed
$feed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" . $getDateString . ".csv";

// Arrays we'll use later
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

// Group data by the "Country_Region" key 
$byGroup = group_by("Country_Region", $newArray);

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