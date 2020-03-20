import React, { useEffect, useState } from 'react';
import './App.css';
import getDatasets from './getDatasets';
import alasql from 'alasql';

function App() {
  const [provinceState, setProvinceState] = useState('New York');
  const [countryRegion, setCountryRegion] = useState('US');
  const [countryRegionsToProvinceStates, setCountryRegionsToProvinceStates] = useState(null);

  useEffect(() => {
    const datasetToTableData = (dataset) => {
      // TODO: Actually generate returned data from passed-in dataset param
      return [
        { provinceState: 'New York', countryRegion: 'US', date: new Date('1/22/20'), cases: '5' },
        { provinceState: 'New York', countryRegion: 'US', date: new Date('1/23/20'), cases: '6' },
        { provinceState: 'New Jersey', countryRegion: 'US', date: new Date('1/22/20'), cases: '10' },
        { provinceState: 'New Jersey', countryRegion: 'US', date: new Date('1/23/20'), cases: '1' },
      ];
    };

    // Set up CSV parser
    getDatasets((confirmedDataset, deathsDataset, recoveredDataset, countryRegionsToProvinceStateMap) => {
      alasql(`DROP TABLE IF EXISTS confirmed`);
      alasql(`DROP TABLE IF EXISTS deaths`);
      alasql(`DROP TABLE IF EXISTS recovered`);

      const columnStatement = '(provinceState STRING, countryRegion STRING, date DATE, cases INT)'; // using 'cases' here instead of 'count' to avoid SQL conflicts
      alasql(`CREATE TABLE confirmed ${columnStatement}`);
      alasql(`CREATE TABLE deaths ${columnStatement}`);
      alasql(`CREATE TABLE recovered ${columnStatement}`);

      alasql.tables.confirmed.data = datasetToTableData(confirmedDataset);
      alasql.tables.deaths.data = datasetToTableData(deathsDataset);
      alasql.tables.recovered.data = datasetToTableData(recoveredDataset);

      // TODO: Use this data to populate dropdown menu in UI, and update provinceState and countryRegion states.
      setCountryRegionsToProvinceStates(countryRegionsToProvinceStateMap);
    });
  }, [provinceState, countryRegion]);

  if(!countryRegionsToProvinceStates) {
    return 'Loading...';
  }

  const renderDatasets = () => {
    return (
      <>
        {
          JSON.stringify(alasql('SELECT * FROM confirmed WHERE provinceState = ? AND countryRegion = ?', [provinceState, countryRegion]))
        }
      </>
    );
  };

  return (
    <div className="App">
      <p>
        I heard you like data!
      </p>
      <p>
        { renderDatasets() }
      </p>
    </div>
  );
}

export default App;
