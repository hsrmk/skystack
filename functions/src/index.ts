import { onDocumentCreated, onDocumentDeleted } from "firebase-functions/v2/firestore";
import * as admin from "firebase-admin";
import { Storage } from "@google-cloud/storage";

admin.initializeApp();
const db = admin.firestore();
const storage = new Storage();

/**
 * Cloud Function: Generate newsletters.json when newsletters are added or removed
 */
const generateNewslettersJson = async () => {
  console.log("Regenerating newsletters.json...");

  try {
    // Fetch all newsletters
    const snapshot = await db.collection("newsletters").get();

    const newsletters = snapshot.docs.map(doc => {
      const data = doc.data();
      const subDomain = data.sub_domain;
      const customDomain = data.custom_domain;

      return {
        profilePicImage: data.logo_url,
        name: data.name,
        username: `${subDomain}.skystack.xyz`,
        description: data.hero_text,
        substackUrl: customDomain
          ? `https://${customDomain}`
          : `https://${subDomain}.substack.com`,
        skystackUrl: `https://bsky.app/profile/${subDomain}.skystack.xyz`,
      };
    });

    // Convert to JSON string
    const jsonData = JSON.stringify(newsletters, null, 2);

    // Upload to Cloud Storage
    const projectId = admin.app().options.projectId;
    const bucket = storage.bucket(`${projectId}.firebasestorage.app`);
    const file = bucket.file("static/newsletters.json");

    await file.save(jsonData, {
      contentType: "application/json",
      public: true, // makes it readable publicly
    });

    console.log("✅ Uploaded static/newsletters.json successfully.");
  } catch (error) {
    console.error("❌ Error generating newsletters.json:", error);
  }
};

// Trigger when a newsletter is added
export const onNewsletterAdded = onDocumentCreated(
  "newsletters/{newsletterId}",
  async (event) => {
    console.log("Newsletter added, regenerating newsletters.json");
    await generateNewslettersJson();
  }
);

// Trigger when a newsletter is removed
export const onNewsletterRemoved = onDocumentDeleted(
  "newsletters/{newsletterId}",
  async (event) => {
    console.log("Newsletter removed, regenerating newsletters.json");
    await generateNewslettersJson();
  }
);
