#include "cards.h"

// Your own deck, if you have one: create lib/core/cards_local.h (git-ignored)
// with one quoted card per line, each followed by a comma. Otherwise the
// short starter set below is used.
#if __has_include("cards_local.h")
static const char *const CARDS[] = {
#include "cards_local.h"
};
#else
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
#endif

static long gcd(long a, long b) { return b ? gcd(b, a % b) : a; }

const char *cardForDay(long localDays) {
  const long n = sizeof(CARDS) / sizeof(CARDS[0]);
  // Step through the deck by a stride that shares no factor with its size, so
  // every card comes up once per pass whatever the deck size.
  long step = 37;
  while (gcd(step, n) != 1) step++;
  return CARDS[((localDays % n) * step % n + n) % n];
}
