using UnityEngine;
using UnityEngine.UI;

using Meta;

using System;
using System.Collections;
using System.Collections.Generic;

namespace CardCounting
{
	public class CardCounter : MonoBehaviour
	{
		//  for color feed texture set value = 0, for depth set value = 1, for ir set value = 2;
		public int sourceDevice = 0;
		private int maxCount = 10;
		private int currentCount;

		public int CurrentCount {
			get { return currentCount; }
			set {
				currentCount = value;
				updateCounter (currentCount);
			}
		}

		private IDictionary<Card, int> seenCards = new Dictionary<Card, int> ();


		// -- Overridden methods --
	
		void Start ()
		{
			Debug.Log ("Start called!");
			//sanity check. espcially if intended to use in Awake() or before that 
			if (DeviceTextureSource.Instance != null && MetaCore.Instance != null) {
				DeviceTextureSource.Instance.registerTextureDevice (sourceDevice);
			}
		}
		
		void Update ()
		{
			if (UnityEngine.Input.GetKeyDown (KeyCode.C)) {
				StartCoroutine (CaptureAndSerializeImage ());
			}
		}


		// -- Private methods --
	
		/// <summary>
		/// Updates the counter with a new seen card.
		/// </summary>
		/// <param name="suit">Suit.</param>
		/// <param name="rank">Rank.</param>
		private void updateCount (CardSuit suit, CardRank rank)
		{
			// Update the list of seen cards.
			Card seenCard =	new Card (suit, rank);
			if (seenCards.ContainsKey (seenCard)) {
				seenCards [seenCard]++;
			} else {
				seenCards [seenCard] = 1;
			}

			// For now, just update the counter.
			if (rank >= CardRank.Ten) {
				CurrentCount--;
			} else {
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
			textComponent.text = newCount.ToString ();

			// Update the color of the text based upon the value of the counter.
			if (CurrentCount == 0) {
				textComponent.color = new Color (1, 1, 1);
			} else if (CurrentCount > 0) {
				float remainder = 1.0f - Math.Max (Math.Abs (CurrentCount), maxCount) / (float)maxCount;
				Debug.Log ("Remainder is: " + remainder + " when count is: " + CurrentCount);

				// Green, because this is a value that you do want to bet high with.
				textComponent.color = new Color (remainder, 1, remainder);
			} else {
				float remainder = 1.0f - Math.Max (Math.Abs (CurrentCount), maxCount) / (float)maxCount;
				Debug.Log ("Remainder is: " + remainder + " when count is: " + CurrentCount);

				// Red, because this is a value that you don't want to bet high with.
				textComponent.color = new Color (1, remainder, remainder);
			}
		}

		/// <summary>
		/// Serialize the texture object and send it over the network.
		/// </summary>
		/// <returns>The image.</returns>
		IEnumerator CaptureAndSerializeImage ()
		{
			// Get the texture.
			if (DeviceTextureSource.Instance.IsDeviceTextureRegistered (sourceDevice)) {
				Texture2D cameraTexture = DeviceTextureSource.Instance.GetDeviceTexture (sourceDevice);

				string url = "http://10.20.8.87:5000/";
				byte[] jpgEncoded = cameraTexture.EncodeToJPG ();
			
				WWWForm form = new WWWForm ();
				form.AddBinaryData ("image", jpgEncoded);
				WWW w = new WWW (url, form);
			
				yield return w;
			
				if (!string.IsNullOrEmpty (w.error)) {
					Debug.LogError (w.error);
				} else {
					Debug.Log ("Finished upload.");
					List<Card> cards = CardUtils.ParseCards (w.text);
					if (cards.Count > 0) {
						updateCount (cards [0].Key, cards [0].Value);
					} else {
						Debug.LogError ("Unrecognized card!");
					}
				}
			} else {
				Debug.LogError ("trying to access unregistered device texture");
			}
		}
	}
}
