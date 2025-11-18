import { onDocumentCreated, onDocumentDeleted } from "firebase-functions/v2/firestore";
import { defineSecret } from "firebase-functions/params";
import * as admin from "firebase-admin";
import { Storage } from "@google-cloud/storage";

admin.initializeApp();
const db = admin.firestore();
const storage = new Storage();

// Define secrets
const STATUS_BSKY_USERNAME = defineSecret("STATUS_BSKY_USERNAME");
const STATUS_BSKY_APP_PASSWORD = defineSecret("STATUS_BSKY_APP_PASSWORD");
const ANNOUNCEMENT_ENDPOINT_TOKEN = defineSecret("ANNOUNCEMENT_ENDPOINT_TOKEN");

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

/**
 * Calls Flask endpoint to create announcement post on Bluesky
 */
const createAnnouncementPost = async (newsletterId: string, eventData: any) => {
  const cloudRunEndpoint = process.env.CLOUD_RUN_ENDPOINT;
  if (!cloudRunEndpoint) {
    console.error("CLOUD_RUN_ENDPOINT environment variable not set");
    return;
  }

  try {
    const endpoint = `${cloudRunEndpoint.replace(/\/$/, "")}/announceNewsletter`;
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${ANNOUNCEMENT_ENDPOINT_TOKEN.value()}`,
      },
      body: JSON.stringify({
        newsletterId,
        custom_domain: eventData.custom_domain || null,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Failed to create announcement post: ${response.status} - ${errorText}`);
    } else {
      console.log("✅ Announcement post created successfully");
    }
  } catch (error) {
    console.error("❌ Error creating announcement post:", error);
  }
};

// Trigger when a newsletter is added
export const onNewsletterAdded = onDocumentCreated(
  {
    document: "newsletters/{newsletterId}",
    secrets: [STATUS_BSKY_USERNAME, STATUS_BSKY_APP_PASSWORD, ANNOUNCEMENT_ENDPOINT_TOKEN],
  },
  async (event) => {
    console.log("Newsletter added, regenerating newsletters.json");
    await generateNewslettersJson();
    
    // Create announcement post
    const newsletterId = event.params.newsletterId;
    const eventData = event.data?.data();
    if (eventData) {
      await createAnnouncementPost(newsletterId, eventData);
    }
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
