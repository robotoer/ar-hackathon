using UnityEngine;
using UnityEngine.UI;

using System;
using System.Collections;
using System.Collections.Generic;

namespace CardCounting {
	public class CardStats : MonoBehaviour {

		// Use this for initialization
		void Start () {
		
		}

		private static Dictionary<CardRank, int> countRanks()
		{
			Dictionary<CardRank, int> counts = new Dictionary<CardRank, int>();
			foreach (Card card in CardRecognizer.Instance.RegisteredCards)
			{
				if (counts.ContainsKey(card.Rank))
				{
					counts[card.Rank]++;
				}
				else
				{
					counts[card.Rank] = 1;
				}
			}

			return counts;
		}
		
		// Update is called once per frame
		void Update () {
			// Update text to represent the current list of seen cards.
			Dictionary<CardRank, int> rankCounts = countRanks();
			string statText = "";
			foreach (CardRank rank in Enum.GetValues(typeof(CardRank)))
			{
				int rankCount = 0;
				if (rankCounts.ContainsKey(rank))
				{
					rankCount = rankCounts[rank];
				}
				statText += rank + ": " + rankCount + "\n";
			}

			Text textComponent = this.GetComponent<Text> ();
			textComponent.text = statText;
		}
	}
}
