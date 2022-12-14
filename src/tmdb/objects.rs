use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct BelongsToCollection {
    pub backdrop_path: String,
    pub id: u64,
    pub name: String,
    pub poster_path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Genre {
    pub id: u64,
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProductionCompany {
    pub id: u64,
    pub logo_path: String,
    pub name: String,
    pub origin_country: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProductionCountry {
    pub iso_3166_1: String,
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SpokenLanguage {
    pub english_name: String,
    pub iso_639_1: String,
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Movie {
    pub adult: bool,
    pub backdrop_path: Option<String>,
    pub belongs_to_collection: Option<BelongsToCollection>,
    pub budget: u64,
    pub genres: Vec<Genre>,
    pub homepage: Option<String>,
    pub id: u64,
    pub imdb_id: String,
    pub original_language: String,
    pub original_title: String,
    pub overview: String,
    pub popularity: f64,
    pub poster_path: String,
    pub production_companies: Vec<ProductionCompany>,
    pub production_countries: Vec<ProductionCountry>,
    pub release_date: String,
    pub revenue: u64,
    pub runtime: u64,
    pub spoken_languages: Vec<SpokenLanguage>,
    pub status: String,
    pub tagline: String,
    pub title: String,
    pub video: bool,
    pub vote_average: f64,
    pub vote_count: u64,
}
