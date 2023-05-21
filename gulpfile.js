const { task, src, dest, parallel } = require('gulp');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const htmlmin = require('gulp-htmlmin');

task('minify-css', () => (
  src('src/static/*.css')
    .pipe(cleanCSS())
    .pipe(dest('dist/static'))
));

task('minify-js', () => (
  src('src/static/*.js')
    .pipe(uglify())
    .pipe(dest('dist/static'))
));

task('minify-html', () => (
  src('src/*.html')
    .pipe(htmlmin({ collapseWhitespace: true }))
    .pipe(dest('dist'))
));

task('copy-lib', () => (
  src('src/lib/**/*')
    .pipe(dest('dist/lib'))
));

task('copy-python', () => (
  src('src/*.py')
    .pipe(dest('dist'))
));

task('default', parallel(
  'minify-css',
  'minify-js',
  'minify-html',
  'copy-lib',
  'copy-python',
));
