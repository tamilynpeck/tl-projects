docker build --rm -t practice:local -f practice_image/Dockerfile .
docker build --rm -t testing:local -f src/test/Dockerfile .
docker run testing:local
