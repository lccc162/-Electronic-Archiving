/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'primary-green': '#006400',
        'header-green': '#004d00',
        'light-green': '#f1f8e9',
        'accent-green': '#4caf50',
      }
    },
  },
  plugins: [],
}
