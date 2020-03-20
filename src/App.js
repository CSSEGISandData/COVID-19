import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {

  const [csvData, setCsvData] = useState(null);

  useEffect(() => {
    axios.get('/data/time_series_19-covid-Confirmed.csv')
      .then(function (response) {
        setCsvData(response.data);
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
        { csvData ? csvData : 'Loading...' }
      </p>
    </div>
  );
}

export default App;
