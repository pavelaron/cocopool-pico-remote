const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const htmlmin = require('gulp-htmlmin');
const { obj } = require('through2');
const { ensureDir } = require('fs-extra');
const { join } = require('path');
const { spawn } = require('child_process');
const {
  task,
  src,
  dest,
  parallel,
} = require('gulp');

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

task('mpy-cross', () => (
  src('src/lib/**/*.py')
    .pipe(obj((chunk, _enc, cb) => {
      const filepath = chunk.path.split('src/lib/').pop();
      const output = filepath.substring(0, filepath.lastIndexOf('.'));
      const outputPath = `dist/lib/${output}.mpy`;

      ensureDir(join(__dirname, 'dist/lib'))
        .then(() => {
          spawn('mpy-cross', [`src/lib/${filepath}`, '-o', outputPath])
            .on('error', cb)
            .on('exit', (code) => {
              console.log('Out:', code, 'Created', outputPath);
              cb(null, chunk);
            });
        })
        .catch(cb);
    }))
));

task('copy-lib', () => (
  src(['src/lib/**/!(*.py)'])
    .pipe(dest('dist/lib'))
));

task('copy-static', () => (
  src(['src/static/**/!(*.css|*.js)'])
    .pipe(dest('dist/static'))
));

task('copy-main', () => (
  src(['src/main.py'])
    .pipe(dest('dist'))
));

task('default', parallel(
  'copy-lib',
  'copy-static',
  'copy-main',
  'mpy-cross',
  'minify-css',
  'minify-js',
  'minify-html',
));
