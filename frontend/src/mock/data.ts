// Fictional reference data for the static (GitHub Pages) demo build.
// Nothing in this file comes from the real database.

export interface ProductRow {
  division: string;
  brand_code: string;
  brand_name: string;
  brand_family_code: string;
  brand_family_name: string;
}

export interface CustomerRow {
  division: string;
  company_code: string;
  country: string;
  channel_code: string;
  channel_name: string;
  subchannel_code: string;
  subchannel_name: string;
  account_code: string;
  account_name: string;
}

export interface UserRow {
  id: number;
  email: string;
  display_name: string | null;
  role: number;
  role_name: string | null;
  ibp_steps: string[] | null;
  is_active: boolean;
  country: Record<string, string> | null;
  division: string[] | null;
}

export const COUNTRY_CODES: Record<string, string> = {
  Australia: "0015",
  "New Zealand": "0014",
};

export const KNOWN_IBP_STEPS = [
  "Portfolio Review",
  "Supply Review",
  "Demand Review",
  "A&P (Pre-Exec)",
  "Overheads (Pre-Exec)",
];

export const LOOKUP_OPTIONS: Record<string, string[]> = {
  division: ["Alcohol", "Non-Alcohol"],
  categorisation: [
    "Volume",
    "Price",
    "Mix",
    "Foreign Exchange",
    "Rebates",
    "Promotions",
    "New Products",
    "Discontinued Products",
    "Other",
  ],
  probability: ["High", "Medium", "Low"],
  status: ["Open", "Approved", "Included in Forecast", "Dismissed", "Archived"],
  ibp_step: KNOWN_IBP_STEPS,
};

const BRANDS: [division: string, code: string, name: string, families: string[]][] = [
  ["Alcohol", "B100", "Jim Beam", ["Jim Beam White", "Jim Beam Black", "Jim Beam RTD"]],
  ["Alcohol", "B110", "Maker's Mark", ["Maker's Mark 46", "Maker's Mark Original"]],
  ["Alcohol", "B120", "Canadian Club", ["Canadian Club Classic", "Canadian Club RTD"]],
  ["Alcohol", "B130", "Laphroaig", ["Laphroaig 10YO", "Laphroaig Quarter Cask"]],
  ["Alcohol", "B140", "-196", ["-196 Lemon", "-196 Grapefruit"]],
  ["Non-Alcohol", "N200", "Coastal Spring", ["Coastal Spring Still", "Coastal Spring Sparkling"]],
  ["Non-Alcohol", "N210", "Kiwi Fizz", ["Kiwi Fizz Original", "Kiwi Fizz Zero"]],
  ["Non-Alcohol", "N220", "Volt Energy", ["Volt Energy Classic", "Volt Energy Sugar Free"]],
];

export const PRODUCTS: ProductRow[] = BRANDS.flatMap(([division, brand_code, brand_name, families]) =>
  families.map((name, i) => ({
    division,
    brand_code,
    brand_name,
    brand_family_code: `${brand_code}-F${i + 1}`,
    brand_family_name: name,
  }))
);

// channel -> subchannel -> accounts (all names are made up)
const CUSTOMER_TREE: [string, string, [string, string, string[]][]][] = [
  ["ONP", "On Premise", [
    ["ONP-HOT", "Hotels", ["Harbourview Hotel Group", "Summit Stays"]],
    ["ONP-BAR", "Bars & Clubs", ["Lantern Bar Collective", "Night Owl Venues"]],
  ]],
  ["OFP", "Off Premise", [
    ["OFP-GRO", "Grocery", ["FreshCart Supermarkets", "Valley Grocers"]],
    ["OFP-LIQ", "Liquor Retail", ["Cellar Door Liquor", "BottleHub"]],
  ]],
  ["ECM", "E-Commerce", [
    ["ECM-DTC", "Direct to Consumer", ["SipDirect Online"]],
  ]],
];

export const CUSTOMERS: CustomerRow[] = (["Alcohol", "Non-Alcohol"] as const).flatMap((division) =>
  Object.entries(COUNTRY_CODES).flatMap(([country, company_code]) =>
    CUSTOMER_TREE.flatMap(([channel_code, channel_name, subs]) =>
      subs.flatMap(([subchannel_code, subchannel_name, accounts]) =>
        accounts.map((account_name, i) => ({
          division,
          company_code,
          country,
          channel_code,
          channel_name,
          subchannel_code,
          subchannel_name,
          account_code: `${company_code}-${subchannel_code}-${i + 1}`,
          account_name: `${account_name} ${country === "Australia" ? "AU" : "NZ"}`,
        }))
      )
    )
  )
);

const ALL_COUNTRIES = { "0015": "Australia", "0014": "New Zealand" };

export const USERS: UserRow[] = [
  { id: 1, email: "demo.admin@example.com", display_name: "Demo Admin", role: 0, role_name: "Admin", ibp_steps: null, is_active: true, country: ALL_COUNTRIES, division: ["Alcohol", "Non-Alcohol"] },
  { id: 2, email: "alex.owner@example.com", display_name: "Alex Owner", role: 1, role_name: "Creator/Owner", ibp_steps: null, is_active: true, country: { "0015": "Australia" }, division: ["Alcohol"] },
  { id: 3, email: "sam.creator@example.com", display_name: "Sam Creator", role: 1, role_name: "Creator/Owner", ibp_steps: null, is_active: true, country: { "0014": "New Zealand" }, division: ["Alcohol", "Non-Alcohol"] },
  { id: 4, email: "jordan.ibp@example.com", display_name: "Jordan IBP", role: 2, role_name: "IBP-Step Approver", ibp_steps: ["Demand Review", "Supply Review"], is_active: true, country: ALL_COUNTRIES, division: ["Alcohol", "Non-Alcohol"] },
  { id: 5, email: "taylor.finance@example.com", display_name: "Taylor Finance", role: 3, role_name: "Finance Approver", ibp_steps: null, is_active: true, country: ALL_COUNTRIES, division: ["Alcohol", "Non-Alcohol"] },
  { id: 6, email: "casey.viewer@example.com", display_name: "Casey Viewer", role: 4, role_name: "Viewer", ibp_steps: null, is_active: true, country: ALL_COUNTRIES, division: ["Alcohol", "Non-Alcohol"] },
];

export const ROLE_NAMES: Record<number, string> = {
  0: "Admin",
  1: "Creator/Owner",
  2: "IBP-Step Approver",
  3: "Finance Approver",
  4: "Viewer",
};

export const DESCRIPTIONS: Record<string, [short: string, long: string][]> = {
  Risk: [
    ["Competitor price cut in grocery", "A competitor has announced deeper shelf discounts for the next quarter, putting pressure on our promoted volume."],
    ["Delayed range review at key account", "The account has pushed its range review back, delaying the listing of two new SKUs."],
    ["Glass supply constraint", "Supplier has flagged reduced bottle availability which may limit production runs."],
    ["Freight cost increase", "Shipping rates on the import lane are trending above plan."],
    ["Excise pass-through timing", "Pricing pass-through of the excise change may lag by one period."],
  ],
  Opportunity: [
    ["Additional promo slot secured", "Customer has offered an extra feature slot during the holiday period."],
    ["New listing win", "Account has confirmed a new listing across its metro stores."],
    ["Favourable FX movement", "Currency movement is improving landed cost on imported product."],
    ["Rebate renegotiation", "Renegotiated rebate tiers reduce trade spend for the remainder of the year."],
    ["Event sponsorship volume", "Sponsored summer events are expected to drive incremental on-premise volume."],
  ],
};
