echo "Authorization: Bearer $TMDB_APIKEY"

# curl --request GET \
#   -v \
#   --url 'https://api.themoviedb.org/3/movie/76341' \
#   --header "Authorization: Bearer $TMDB_APIKEY" \
#   --header 'Content-Type: application/json;charset=utf-8' | jq


# curl --request GET \
#   -v \
#   --url 'https://api.themoviedb.org/3/search/movie?query=Interstellar' \
#   --header "Authorization: Bearer $TMDB_APIKEY" \
#   --header 'Content-Type: application/json;charset=utf-8' | jq

curl --request GET \
  -v \
  --url "https://api.themoviedb.org/3/movie/76341?api_key=${TMDB_APIKEY}" | jq