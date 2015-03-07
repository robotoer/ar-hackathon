using UnityEngine;
using UnityEngine.UI;

using Meta;

using System;
using System.Collections;
using System.Collections.Generic;
using System.Xml;

using SimpleJSON;

public enum CardSuit {
	Spade,
	Club,
	Heart,
	Diamond
}

public enum CardRank {
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

public class CardCounter : MonoBehaviour {
	//  for color feed texture set value = 0, for depth set value = 1, for ir set value = 2;
	public int sourceDevice = 0;

	private int maxCount = 10;
	private int currentCount;
	public int CurrentCount {
		get { return currentCount; }
		set {
			currentCount = value;
			updateCounter(currentCount);
		}
	}

	private IDictionary<KeyValuePair<CardSuit, CardRank>, int> seenCards = 
		new Dictionary<KeyValuePair<CardSuit, CardRank>, int>();

	void Start()
	{
		Debug.Log("Start called!");
		//sanity check. espcially if intended to use in Awake() or before that 
		if (DeviceTextureSource.Instance != null && MetaCore.Instance != null)
		{
			DeviceTextureSource.Instance.registerTextureDevice(sourceDevice);
		}
	}
		
	void Update()
	{
		if (UnityEngine.Input.GetKeyDown(KeyCode.C))
		{
			StartCoroutine(CaptureAndSerializeImage());
		}
	}

	CardSuit ParseSuit(string suit)
	{
		switch (suit)
		{
		case "H":
			return CardSuit.Heart;
		case "S":
			return CardSuit.Spade;
		case "C":
			return CardSuit.Club;
		case "D":
			return CardSuit.Diamond;
		}
		throw new Exception("Unrecognized card suit: " + suit);
	}

	CardRank ParseRank(string rank)
	{
		switch (rank)
		{
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
		throw new Exception("Unrecognized card rank: " + rank);
	}

	void ParseJson(string json)
	{
		JSONNode jsonTree = JSON.Parse(json);
		CardSuit suit = ParseSuit(jsonTree["suit"].Value);
		CardRank rank = ParseRank(jsonTree["rank"].Value);
		Debug.Log("Recognized card: " + rank + " of " + suit);
		if (suit != null && rank != null)
		{
			UpdateCount(suit, rank);
		}
		else
		{
			Debug.LogError("Unrecognized card!");
		}
	}

	/// <summary>
	/// Updates the counter with a new seen card.
	/// </summary>
	/// <param name="suit">Suit.</param>
	/// <param name="rank">Rank.</param>
	void UpdateCount(CardSuit suit, CardRank rank)
	{
		// Update the list of seen cards.
		KeyValuePair<CardSuit, CardRank> seenCard =
			new KeyValuePair<CardSuit, CardRank>(suit, rank);
		if (seenCards.ContainsKey(seenCard))
		{
			seenCards[seenCard]++;
		}
		else
		{
			seenCards[seenCard] = 1;
		}

		// For now, just update the counter.
		if (rank >= CardRank.Ten)
		{
			CurrentCount--;
		}
		else
		{
			CurrentCount++;
		}
	}

	/// <summary>
	/// Updates the counter's textual representation with a new value.
	/// </summary>
	/// <param name="newCount">New counter value.</param>
	private void updateCounter (int newCount)
	{
		// Update the text of the counter.
		Text textComponent = this.GetComponent<Text> ();
		textComponent.text = newCount.ToString();

		// Update the color of the text based upon the value of the counter.
		if (CurrentCount == 0)
		{
			textComponent.color = new Color(1, 1, 1);
		}
		else if (CurrentCount > 0)
		{
			float remainder = 1.0f - Math.Max(Math.Abs(CurrentCount), maxCount) / (float)maxCount;
			Debug.Log("Remainder is: " + remainder + " when count is: " + CurrentCount);

			// Green, because this is a value that you do want to bet high with.
			textComponent.color = new Color(remainder, 1, remainder);
		}
		else
		{
			float remainder = 1.0f - Math.Max(Math.Abs(CurrentCount), maxCount) / (float)maxCount;
			Debug.Log("Remainder is: " + remainder + " when count is: " + CurrentCount);

			// Red, because this is a value that you don't want to bet high with.
			textComponent.color = new Color(1, remainder, remainder);
		}
	}

	/// <summary>
	/// Serialize the texture object and send it over the network.
	/// </summary>
	/// <returns>The image.</returns>
	IEnumerator CaptureAndSerializeImage()
	{
		// Get the texture.
		if (DeviceTextureSource.Instance.IsDeviceTextureRegistered(sourceDevice))
		{
			Texture2D cameraTexture = DeviceTextureSource.Instance.GetDeviceTexture(sourceDevice);

			string url = "http://10.20.8.20:5000/";
			byte[] jpgEncoded = cameraTexture.EncodeToJPG();
			
			WWWForm form = new WWWForm();
			form.AddBinaryData("image", jpgEncoded);
			WWW w = new WWW(url, form);
			
			yield return w;
			
			if (!string.IsNullOrEmpty(w.error)) {
				Debug.LogError(w.error);
			} else {
				Debug.Log("Finished upload.");
				ParseJson(w.text);
			}
		}
		else
		{
			Debug.LogError("trying to access unregistered device texture");
		}
	}
}
