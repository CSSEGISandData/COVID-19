import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';
import csvParse from 'csv-parse';

function App() {
  const [dataset, setDataset] = useState(null);

  useEffect(() => {
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

    axios.get('/data/time_series_19-covid-Confirmed.csv')
      .then(function (response) {
        setDataset(parseCsvData(response.data));
      })
      .catch(function (error) {
        console.log(error);
      });
  }, []);

  return (
    <div className="App">
      <p>
        I heard you like data!
      </p>
      <p>
        { dataset ? JSON.stringify(dataset) : 'Loading...' }
      </p>
    </div>
  );
}

export default App;
