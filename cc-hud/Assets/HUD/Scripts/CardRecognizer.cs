//------------------------------------------------------------------------------
// Code related to keeping track of the set of seen cards.
//------------------------------------------------------------------------------

using System;
using System.Collections;
using System.Collections.Generic;

namespace CardCounting
{
	/// <summary>
	/// Class for recognizing cards from a deck.
	/// 
	/// Stores state related to recognizing cards from a deck.
	/// 
	/// Assumptions:
	/// - There is only one deck of cards.
	/// 
	/// Terminology:
	/// - Seen card (card that has been recognized in a single image).
	/// - Registered card (card that has been seen enough to mark it as definitely seen).
	/// </summary>
	public class CardRecognizer
	{
		// -- Static stuff --
		private static CardRecognizer instance = new CardRecognizer();
		public static CardRecognizer Instance { get { return instance; } }

		private HashSet<Card> registeredCards = new HashSet<Card>();
		private Dictionary<Card, List<DateTime>> seenCards = new Dictionary<Card, List<DateTime>>();

		public HashSet<Card> RegisteredCards { get { return registeredCards; } }

		private static bool cardSeenEnough(DateTime currentTime, List<DateTime> observations)
		{
			// If the card has been seen more than 4 times in the past 30 seconds, mark the card as registered.
			int recentObservationCount = 0;
			foreach (DateTime observation in observations)
			{
				if (currentTime.Subtract(observation) <= TimeSpan.FromSeconds(30))
				{
					recentObservationCount++;
				}
			}

			return recentObservationCount > 4;
		}

		// Add new seen raw cards.
		public HashSet<Card> ObserveCards(DateTime timestamp, ICollection<Card> rawCards)
		{
			HashSet<Card> newRegisteredCards = new HashSet<Card>();

			// Update dictionary of seen cards raw.
			foreach (Card card in rawCards)
			{
				if (!seenCards.ContainsKey(card))
				{
					seenCards[card] = new List<DateTime>();
				}
				seenCards[card].Add(timestamp);

				// Check to see if any cards can be marked as "seen".
				if (cardSeenEnough(timestamp, seenCards[card]))
				{
					if (!registeredCards.Contains(card))
					{
						registeredCards.Add (card);
						newRegisteredCards.Add (card);
					}
				}
			}

			// Return new seen cards.
			return newRegisteredCards;
		}
	}
}

