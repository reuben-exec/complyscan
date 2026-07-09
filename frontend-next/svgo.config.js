module.exports = {
  multipass: true,
  plugins: [
    'preset-default',
    'removeDimensions',
    {
      name: 'convertPathData',
      params: {
        floatPrecision: 2,
      },
    },
    {
      name: 'mergePaths',
      params: {
        force: true,
      },
    },
    'removeOffCanvasPaths',
    'collapseGroups',
  ],
};
