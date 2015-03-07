//------------------------------------------------------------------------------
// Utility methods/classes/enums for card counting.
//------------------------------------------------------------------------------
using System;
using System.Collections.Generic;

using SimpleJSON;

namespace CardCounting
{
	/// <summary>
	/// Card suit.
	/// </summary>
	public enum CardSuit
	{
		Spade,
		Club,
		Heart,
		Diamond
	}
	
	/// <summary>
	/// Card rank.
	/// </summary>
	public enum CardRank
	{
		Two = 2,
		Three = 3,
		Four = 4,
		Five = 5,
		Six = 6,
		Seven = 7,
		Eight = 8,
		Nine = 9,
		Ten = 10,
		Jack = 11,
		Queen = 12,
		King = 13,
		Ace = 14
	}
	
	/// <summary>
	/// Card utility methods.
	/// </summary>
	public static class CardUtils
	{
		/// <summary>
		/// Parses the card suit from a string.
		/// </summary>
		/// <returns>The suit.</returns>
		/// <param name="suit">Suit as a string.</param>
		public static CardSuit ParseSuit (string suit)
		{
			switch (suit) {
			case "H":
				return CardSuit.Heart;
			case "S":
				return CardSuit.Spade;
			case "C":
				return CardSuit.Club;
			case "D":
				return CardSuit.Diamond;
			}
			throw new Exception ("Unrecognized card suit: " + suit);
		}
		
		/// <summary>
		/// Parses the card rank from a string.
		/// </summary>
		/// <returns>The rank.</returns>
		/// <param name="rank">Rank as a string.</param>
		public static CardRank ParseRank (string rank)
		{
			switch (rank) {
			case "A":
				return CardRank.Ace;
			case "2":
				return CardRank.Two;
			case "3":
				return CardRank.Three;
			case "4":
				return CardRank.Four;
			case "5":
				return CardRank.Five;
			case "6":
				return CardRank.Six;
			case "7":
				return CardRank.Seven;
			case "8":
				return CardRank.Eight;
			case "9":
				return CardRank.Nine;
			case "10":
				return CardRank.Ten;
			case "J":
				return CardRank.Jack;
			case "Q":
				return CardRank.Queen;
			case "K":
				return CardRank.King;
			}
			throw new Exception ("Unrecognized card rank: " + rank);
		}
		
		/// <summary>
		/// Parses the json representation of recognized cards.
		/// </summary>
		/// <returns>A list of recognized cards.</returns>
		/// <param name="json">Json representation of a list of recognized cards.</param>
		public static List<KeyValuePair<CardSuit, CardRank>> ParseJson (string json)
		{
			JSONNode jsonTree = JSON.Parse (json);
			CardSuit suit = ParseSuit (jsonTree ["suit"].Value);
			CardRank rank = ParseRank (jsonTree ["rank"].Value);
			Debug.Log ("Recognized card: " + rank + " of " + suit);
			List<KeyValuePair<CardSuit, CardRank>> cards = new List<KeyValuePair<CardSuit, CardRank>> ();
			if (suit != null && rank != null) {
				cards.Add (new KeyValuePair<CardSuit, CardRank> (suit, rank));
			}
			return cards;
		}
	}
}
