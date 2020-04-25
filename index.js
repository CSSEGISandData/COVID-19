const Papa = require('papaparse');
const fs = require('fs');

const filename = 'time_series_19-covid-Confirmed.csv';
const path = './csse_covid_19_data/csse_covid_19_time_series/' + 'time_series_covid19_confirmed_global.csv';

const outputDir = 'output/';
const outputPath = outputDir + filename;

const expectedHeader = ['Province/State', 'Country/Region', 'Lat', 'Long', '1/22/20', '1/23/20', '1/24/20', '1/25/20', '1/26/20', '1/27/20', '1/28/20', '1/29/20', '1/30/20', '1/31/20', '2/1/20', '2/2/20', '2/3/20', '2/4/20', '2/5/20', '2/6/20', '2/7/20', '2/8/20', '2/9/20', '2/10/20', '2/11/20', '2/12/20', '2/13/20', '2/14/20', '2/15/20', '2/16/20', '2/17/20', '2/18/20', '2/19/20', '2/20/20', '2/21/20', '2/22/20', '2/23/20', '2/24/20', '2/25/20', '2/26/20', '2/27/20', '2/28/20', '2/29/20'];

const FAIL = 1;

// Add promise to papa
Papa.parsePromise = function(file) {
  return new Promise(function(resolve, reject) {
    Papa.parse(file, {complete: resolve, error: reject});
  });
};

const writeOutput = (path, outputPath) => {
  fs.copyFileSync(path, outputPath);
};

const validateCopy = (path, outputPath) => {
  console.log(`validating ${path}`);

  if (fs.existsSync(path)) {
    console.log('file exists');
    const file = fs.createReadStream(path);
    Papa.parsePromise(file, {
      complete: function(results) {

      }
    })
      .then(results => {
        console.log('parse completed, parsing results');
        const data = results.data;
        const header = data[0];
        for (const [i, expected] of expectedHeader.entries()) {
          const value = header[i];
          if (value != expected) {
            console.log(`unexpected header ${value}, expected: ${expected}`);
            return FAIL;
          } else {
            console.log(`header ${i} matches: ${value}`);
          }
        }

        if (header.length > expectedHeader.length) {
          console.warn(`file header is longer than validation list: ${header.length} vs ${expectedHeader.length}`);
          console.warn('not everyting is checked!');
          for (let i = expectedHeader.length; i < header.length; ++i) {
            console.log(`extra header ${i}: ${header[i]}`);
          }
        }

        console.log(`validation success, writing ${outputPath}`);
        writeOutput(path, outputPath)
      })
      .then(() => {
        // Double check output written:
        if (fs.existsSync(outputPath)) {
          console.log('output file exists: ', outputPath);
        } else {
          throw new Error(`missing output file ${outputPath}`)
        }
      });
  } else {
    console.error('file does not exist: ');
    throw new Error(`file does not exist ${path}`);
  }


};


//
//
//
if (!fs.existsSync(outputDir)){
  fs.mkdirSync(outputDir);
}
fs.copyFileSync('README.md', outputDir + 'README.md');

validateCopy(path, outputPath);

console.log('end of index.js');
