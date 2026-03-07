/**
 * Festival calendar for Raju Bhai's store (Indore).
 * Dates match events.json on S3 - updated via Calendar API.
 * EventBridge Lambda runs daily; alert timing and days-before are user-configurable (set in chat).
 */
export const FESTIVAL_CALENDAR = [
  {
    id: "holi-2026",
    name: "Holi",
    date: "2026-03-03",
    type: "festival",
    hinglishAlert: "Raju Bhai, Holi aane wali hai! Gulal, Ghee aur Shakkar ka stock check kar lijiye.",
    stockTip: "Order Gulal, Ghee, Shakkar, Thandai masala",
  },
  {
    id: "chaitra-navratri-2026",
    name: "Chaitra Navratri",
    date: "2026-03-19",
    type: "festival",
    hinglishAlert: "Raju Bhai, Navratri shuru hone wali hai! Sabudana aur Singhara aata ka stock badha lo!",
    stockTip: "Order Sabudana, Singhara aata, Rock salt, Fruits",
  },
  {
    id: "indore-wedding-season-mar-2026",
    name: "Wedding Season (Indore)",
    date: "2026-03-15",
    type: "local",
    hinglishAlert: "Raju Bhai, Indore mein shaadi ka season aa raha hai! Dry fruits aur gifting items ka stock check karo!",
    stockTip: "Stock up on Dry fruits, Mithai boxes, Gift packs",
  },
  {
    id: "raksha-bandhan-2026",
    name: "Raksha Bandhan",
    date: "2026-08-28",
    type: "festival",
    hinglishAlert: "Raju Bhai, Raksha Bandhan aane wala hai! Mithai aur Chocolates ka stock ready rakho!",
    stockTip: "Order Mithai, Chocolates, Gift boxes, Rakhi accessories",
  },
  {
    id: "diwali-2026",
    name: "Diwali",
    date: "2026-11-08",
    type: "festival",
    hinglishAlert: "Raju Bhai, Diwali aane wali hai! Mithai, Dry Fruits aur Gift packs ka stock prepare kar lo!",
    stockTip: "Order Mithai, Dry fruits, Diyas, Gift boxes, Namkeen",
  },
  {
    id: "indore-diwali-shopping-2026",
    name: "Diwali Shopping Rush (Indore)",
    date: "2026-11-01",
    type: "local",
    hinglishAlert: "Raju Bhai, Diwali shopping rush shuru hone wala hai! Store mein sab kuch ready rakho!",
    stockTip: "Ensure all Diwali stock is ready a week before",
  },
]

/** Days before a festival to start showing alerts in the UI */
export const FESTIVAL_ALERT_DAYS = 5
