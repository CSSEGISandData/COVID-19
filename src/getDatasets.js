import axios from 'axios';
import csvParse from 'csv-parse';

const PROVINCE_STATE_COLUMN = 0;
const COUNTRY_REGION_COLUMN = 1;

// Set up CSV parser
const parseCsvData = (data) => {
  const csvParser = csvParse();
  const csvArr = [];

  // Use the readable stream api
  csvParser.on('readable', function(){
    let record;
    while ((record = csvParser.read())) {
      csvArr.push(record)
    }
  });
  // Catch any error
  csvParser.on('error', function(err){
    console.error(err.message)
  });
  // Send data to read to the stream
  csvParser.write(data);

  // Return the CSV as a 2D array
  return csvArr;
};


/**
 * Callback for retrieving dataset data.
 *
 * @callback datasetsCallback
 * @param {string[][]} confirmedData -
 * @param {string[][]} deathsData -
 * @param {string[][]} recoveredData -
 */

/**
 * Retrieves the primary datasets for the my-corona app.
 *
 * @param {datasetsCallback} callback - A callback to run.
 */
const getDatasets = (callback) => {
  axios.all([
    axios.get('/data/time_series_19-covid-Confirmed.csv'),
    axios.get('/data/time_series_19-covid-Deaths.csv'),
    axios.get('/data/time_series_19-covid-Recovered.csv')
  ]).then(axios.spread((confirmedResponse, deathsResponse, recoveredResponse) => {
    let confirmedDataset = parseCsvData(confirmedResponse.data);
    let deathsDataset = parseCsvData(deathsResponse.data);
    let recoveredDataset = parseCsvData(recoveredResponse.data);



    let countryRegionsToProvinceStates = {};
    confirmedDataset.forEach((row, i) => {
      if(i === 0) return;
      const countryRegion = row[COUNTRY_REGION_COLUMN];
      const provinceState = row[PROVINCE_STATE_COLUMN];

      if(!countryRegion) return;
      countryRegionsToProvinceStates[countryRegion] = countryRegionsToProvinceStates[countryRegion] || [];
      if(!provinceState) return;
      countryRegionsToProvinceStates[countryRegion].push(provinceState);
    });
    callback(
      confirmedDataset,
      deathsDataset,
      recoveredDataset,
      countryRegionsToProvinceStates
    );
  })).catch(function (error) {
    console.log(error);
  });
};

export default getDatasets;
