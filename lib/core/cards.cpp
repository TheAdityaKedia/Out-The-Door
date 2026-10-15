#include "cards.h"

// A short starter set. Add the rest of the deck (or your own cards) here.
static const char *const CARDS[] = {
    "Honor thy error as a hidden intention",
    "Use an old idea",
    "What would your closest friend do?",
    "Emphasize differences",
    "Do nothing for as long as possible",
    "Look closely at the most embarrassing details and amplify them",
    "Repetition is a form of change",
    "Work at a different speed",
    "Go slowly all the way round the outside",
    "Discard an axiom",
    "Be the first not to do what has never not been done before",
    "Only one element of each kind",
    "Ask your body",
    "Gardening, not architecture",
};

const char *cardForDay(long localDays) {
  const long n = sizeof(CARDS) / sizeof(CARDS[0]);
  return CARDS[((localDays * 37) % n + n) % n];
}
