APIKEY=$(cat ../tmdb_apikey.secret)

echo "Authorization: Bearer $APIKEY"

curl --request GET \
  -v \
  --url 'https://api.themoviedb.org/3/movie/76341' \
  --header "Authorization: Bearer $APIKEY" \
  --header 'Content-Type: application/json;charset=utf-8' | jq