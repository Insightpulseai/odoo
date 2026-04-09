# Meta Marketing API — Production Integration Map

> For InsightPulseAI ad automation across Facebook, Instagram, Messenger, WhatsApp.
> Covers: auth, core objects, endpoints, token/scopes, backend service shape.

---

## 1. Auth Flow

### Token types

| Token | Use | How to get |
|-------|-----|------------|
| User Access Token | Dev/testing, own ad account | Graph API Explorer |
| System User Token | Production automation | Business Manager → System Users |
| Page Access Token | Posting ads from a Page | Exchange user token via `/me/accounts` |

### Required permissions (scopes)

| Permission | Purpose | Requires App Review? |
|------------|---------|---------------------|
| `ads_management` | Create/modify/delete campaigns, ad sets, ads | Yes (screencast required) |
| `ads_read` | Read-only access to ad insights | Yes |
| `pages_manage_posts` | Post ads from a Page | Yes |
| `pages_read_engagement` | Read Page metadata (dependency) | Yes |
| `pages_show_list` | List managed Pages (dependency) | Yes |
| `public_profile` | Basic user info | Auto-granted |

### App Review bypass for own account

For managing **your own** ad account only (not third-party):
- Standard Access is sufficient for `ads_management`
- No screencast needed
- Generate token via Graph API Explorer with permissions checked
- Works immediately for `act_<YOUR_AD_ACCOUNT_ID>`

### System User (production)

1. Business Manager → Settings → Users → System Users → Add
2. Assign ad account + Page assets
3. Generate token with `ads_management` + `pages_manage_posts`
4. Token does not expire (until revoked)

---

## 2. Ad Object Hierarchy

```
Ad Account (act_XXXX)
  └── Campaign (objective, budget type)
       └── Ad Set (targeting, budget, schedule, optimization)
            └── Ad (creative + placement)
                 └── Ad Creative (image/video, copy, CTA, URL)
```

Each level has its own API endpoint under the ad account.

---

## 3. Core Endpoints

### Campaign

```bash
# Create
POST /act_{AD_ACCOUNT_ID}/campaigns
  name, objective, status, special_ad_categories

# Read
GET /{CAMPAIGN_ID}?fields=name,objective,status

# Update
POST /{CAMPAIGN_ID}
  status=PAUSED

# Delete
DELETE /{CAMPAIGN_ID}
```

**Objectives** (v21.0+):
- `OUTCOME_TRAFFIC` — drive website visits
- `OUTCOME_ENGAGEMENT` — post engagement
- `OUTCOME_LEADS` — lead generation
- `OUTCOME_SALES` — conversions/purchases
- `OUTCOME_AWARENESS` — reach/impressions

### Ad Set

```bash
# Create
POST /act_{AD_ACCOUNT_ID}/adsets
  name, campaign_id, daily_budget (in cents),
  billing_event=IMPRESSIONS, optimization_goal=LINK_CLICKS,
  targeting, start_time, end_time, status

# Targeting example
targeting={
  "geo_locations": {"countries": ["PH","US","GB","AU"]},
  "age_min": 25, "age_max": 55,
  "interests": [
    {"id": "6003139266461", "name": "Clinical research"},
    {"id": "6003397425735", "name": "Evidence-based medicine"}
  ]
}
```

### Ad Creative

```bash
# Upload image first
POST /act_{AD_ACCOUNT_ID}/adimages
  filename=@/path/to/image.png

# Returns image_hash

# Create creative
POST /act_{AD_ACCOUNT_ID}/adcreatives
  name, object_story_spec={
    "page_id": "PAGE_ID",
    "link_data": {
      "image_hash": "IMAGE_HASH",
      "link": "https://prismalab.insightpulseai.com",
      "message": "Ad text here...",
      "name": "Headline here",
      "description": "Description here",
      "call_to_action": {"type": "BOOK_TRAVEL", "value": {"link": "https://insightpulseai.zohobookings.com"}}
    }
  }
```

### Ad

```bash
# Create ad (links creative to ad set)
POST /act_{AD_ACCOUNT_ID}/ads
  name, adset_id, creative={"creative_id": "CREATIVE_ID"},
  status=PAUSED
```

---

## 4. Full Campaign Creation Sequence

```python
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adimage import AdImage

# Init
FacebookAdsApi.init(app_id='APP_ID', app_secret='APP_SECRET', access_token='TOKEN')
account = AdAccount('act_1491166555865337')

# 1. Upload image
image = AdImage(parent_id=account.get_id())
image[AdImage.Field.filename] = '/path/to/meta-ad-square.png'
image.remote_create()
image_hash = image[AdImage.Field.hash]

# 2. Create campaign
campaign = Campaign(parent_id=account.get_id())
campaign.update({
    Campaign.Field.name: 'PrismaLab - Systematic Review Consulting',
    Campaign.Field.objective: 'OUTCOME_TRAFFIC',
    Campaign.Field.status: 'PAUSED',
    Campaign.Field.special_ad_categories: [],
})
campaign.remote_create()

# 3. Create ad set
adset = AdSet(parent_id=account.get_id())
adset.update({
    AdSet.Field.name: 'PrismaLab - Researchers 25-55',
    AdSet.Field.campaign_id: campaign.get_id(),
    AdSet.Field.daily_budget: 50000,  # in cents (500 PHP)
    AdSet.Field.billing_event: 'IMPRESSIONS',
    AdSet.Field.optimization_goal: 'LINK_CLICKS',
    AdSet.Field.targeting: {
        'geo_locations': {'countries': ['PH', 'US', 'GB', 'AU']},
        'age_min': 25,
        'age_max': 55,
        'interests': [
            {'id': '6003139266461', 'name': 'Clinical research'},
            {'id': '6003397425735', 'name': 'Evidence-based medicine'},
        ],
    },
    AdSet.Field.status: 'PAUSED',
})
adset.remote_create()

# 4. Create creative
creative = AdCreative(parent_id=account.get_id())
creative.update({
    AdCreative.Field.name: 'PrismaLab Hero Ad',
    AdCreative.Field.object_story_spec: {
        'page_id': '1076156775589182',
        'link_data': {
            'image_hash': image_hash,
            'link': 'https://prismalab.insightpulseai.com',
            'message': 'Struggling with your systematic review? We handle the methodology so you can focus on the science.\n\nPRISMA 2020-compliant systematic reviews and meta-analyses — from protocol to publication.\n\nBook a free consult today.',
            'name': 'PRISMA-Compliant Systematic Reviews',
            'description': 'Expert meta-analysis consulting for researchers and clinicians.',
            'call_to_action': {
                'type': 'BOOK_TRAVEL',
                'value': {'link': 'https://insightpulseai.zohobookings.com'},
            },
        },
    },
})
creative.remote_create()

# 5. Create ad
ad = Ad(parent_id=account.get_id())
ad.update({
    Ad.Field.name: 'PrismaLab - Main Ad',
    Ad.Field.adset_id: adset.get_id(),
    Ad.Field.creative: {'creative_id': creative.get_id()},
    Ad.Field.status: 'PAUSED',
})
ad.remote_create()

print(f'Campaign: {campaign.get_id()}')
print(f'Ad Set: {adset.get_id()}')
print(f'Creative: {creative.get_id()}')
print(f'Ad: {ad.get_id()}')
# Change status to ACTIVE to go live
```

---

## 5. Insights / Reporting

```bash
# Campaign insights
GET /{CAMPAIGN_ID}/insights?fields=impressions,clicks,spend,cpc,ctr,reach
  &date_preset=last_7d

# Ad-level insights
GET /{AD_ID}/insights?fields=impressions,clicks,spend,actions
  &breakdowns=age,gender,country
```

---

## 6. Adjacent APIs

| API | When to add | Endpoint |
|-----|-------------|----------|
| Conversions API | Server-side event tracking for better attribution | `POST /{PIXEL_ID}/events` |
| Catalog API | Product ads / dynamic creative | `POST /{CATALOG_ID}/products` |
| Business Management API | Multi-account management | `POST /{BUSINESS_ID}/...` |

---

## 7. Rate Limits

| Tier | Limit |
|------|-------|
| Standard | 200 calls/hour/ad account |
| Insights | 60 calls/hour/ad account |
| Batch | Up to 50 requests per batch call |

Use batch requests for bulk operations:
```bash
POST /
  batch=[{"method":"POST","relative_url":"act_XXX/campaigns","body":"name=..."},...]
```

---

## 8. InsightPulseAI Integration

| Component | Value |
|-----------|-------|
| Ad Account | `act_1491166555865337` |
| Page ID | `1076156775589182` |
| App ID | `951394464039117` |
| Landing URL | `https://prismalab.insightpulseai.com` |
| Booking URL | `https://insightpulseai.zohobookings.com` |
| SDK installed | `facebook_business==25.0.0` (pyenv `odoo-18-dev`) |
| Token status | `public_profile` only — needs `ads_management` via System User or App Review |

### Next step to unlock API access

Create a **System User** in Business Manager:
1. Business Settings → Users → System Users → Add
2. Role: Admin
3. Assign: ad account `act_1491166555865337` + Page `Insightpulseai`
4. Generate token with `ads_management` + `pages_manage_posts`
5. Save token in Azure Key Vault as `meta-ads-system-token`

---

## References

- Marketing API: https://developers.facebook.com/docs/marketing-api
- Graph API Explorer: https://developers.facebook.com/tools/explorer/
- Permissions Reference: https://developers.facebook.com/docs/permissions/reference
- Meta Business SDK (Python): https://github.com/facebook/facebook-python-business-sdk
