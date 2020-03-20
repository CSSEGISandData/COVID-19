const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = function override(config, env) {
    if (!config.plugins) {
        config.plugins = [];
    }

    config.plugins.push(
        new CopyWebpackPlugin([
          { from: 'csse_covid_19_data/csse_covid_19_time_series', to: './data' },
      ])
    );

    return config;
}
