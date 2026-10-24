// BART real-time departures (legacy JSON API, cmd=etd).
#pragma once
#include "types.h"

// Writes the request URL into out.
void bartUrl(const char *station, const char *key, char *out, int size);

// Fills one TrainRow per configured row from the API's JSON. Trains already
// "Leaving", cancelled trains, and destinations in no row are left out.
// Returns false if the JSON could not be read.
bool parseBart(const char *json, const TrainRowConfig *rows, int rowCount, TrainRow *out);

// Counts down rows fetched ageSeconds ago, dropping trains that have gone.
TrainRow countDown(const TrainRow &row, long ageSeconds);
