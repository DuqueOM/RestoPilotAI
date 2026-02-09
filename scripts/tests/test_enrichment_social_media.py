"""
Integration tests for social media and delivery platform enrichment.

Verifies that the enrichment pipeline correctly discovers and validates
social media URLs and delivery platform pages for known restaurants.

Reference data from: docs/Demo/general information.md
"""

import asyncio
import sys

# Expected values for "Margarita Pinta" (Pasto, Colombia)
EXPECTED = {
    "place_id": "ChIJuSMfewDVLo4Roc6ycTAVK3k",
    "name": "Margarita Pinta",
    "address": "Cl 20 #40A-10, Pasto, Nariño, Colombia",
    "facebook": "https://www.facebook.com/MargaritaPintaRestauranteBar",
    "instagram": "https://www.instagram.com/margaritapintapasto/",
    "rappi": "https://www.rappi.com.co/restaurantes/900178500-margarita-pinta",
}


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (strip trailing slash, lowercase scheme+host)."""
    if not url:
        return ""
    return url.rstrip("/")


async def test_facebook_probing():
    """Test deterministic Facebook URL discovery via candidate probing."""
    from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
    from app.core.config import get_settings

    settings = get_settings()
    svc = CompetitorEnrichmentService(google_maps_api_key=settings.google_maps_api_key)

    try:
        fb_url = await svc._discover_facebook_page(
            name="Margarita Pinta",
            city="Pasto",
            gemini_social_data={},
        )
        expected = EXPECTED["facebook"]
        assert fb_url is not None, "Facebook URL should not be None"
        assert normalize_url(fb_url) == normalize_url(expected), (
            f"Facebook URL mismatch: got {fb_url}, expected {expected}"
        )
        print("✓ test_facebook_probing PASSED")
        return True
    except AssertionError as e:
        print(f"✗ test_facebook_probing FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ test_facebook_probing ERROR: {e}")
        return False
    finally:
        await svc.close()


async def test_instagram_probing():
    """Test deterministic Instagram handle discovery via candidate probing."""
    from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
    from app.core.config import get_settings

    settings = get_settings()
    svc = CompetitorEnrichmentService(google_maps_api_key=settings.google_maps_api_key)

    try:
        ig_url = await svc._probe_instagram_handle(
            name="Margarita Pinta",
            city="Pasto",
        )
        expected = EXPECTED["instagram"]
        assert ig_url is not None, "Instagram URL should not be None"
        assert normalize_url(ig_url) == normalize_url(expected), (
            f"Instagram URL mismatch: got {ig_url}, expected {expected}"
        )
        print("✓ test_instagram_probing PASSED")
        return True
    except AssertionError as e:
        print(f"✗ test_instagram_probing FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ test_instagram_probing ERROR: {e}")
        return False
    finally:
        await svc.close()


async def test_rappi_discovery():
    """Test Rappi store URL discovery via DDG Lite search + slug scoring."""
    from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
    from app.core.config import get_settings

    settings = get_settings()
    svc = CompetitorEnrichmentService(google_maps_api_key=settings.google_maps_api_key)

    try:
        import re
        name_slug = re.sub(r'[^a-z0-9]+', '-', "Margarita Pinta".lower()).strip('-')
        rappi_url = await svc._discover_rappi_store(
            business_name="Margarita Pinta",
            business_address=EXPECTED["address"],
            city_hint="Pasto",
            name_slug=name_slug,
        )
        expected = EXPECTED["rappi"]
        assert rappi_url is not None, "Rappi URL should not be None"
        assert normalize_url(rappi_url) == normalize_url(expected), (
            f"Rappi URL mismatch: got {rappi_url}, expected {expected}"
        )
        print("✓ test_rappi_discovery PASSED")
        return True
    except AssertionError as e:
        print(f"✗ test_rappi_discovery FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ test_rappi_discovery ERROR: {e}")
        return False
    finally:
        await svc.close()


async def test_full_enrichment():
    """Test the complete enrichment pipeline returns correct social media and delivery URLs."""
    from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
    from app.core.config import get_settings

    settings = get_settings()
    svc = CompetitorEnrichmentService(google_maps_api_key=settings.google_maps_api_key)

    try:
        profile = await svc.enrich_competitor_profile(EXPECTED["place_id"])

        # Verify name and address
        assert profile.name == EXPECTED["name"], f"Name mismatch: {profile.name}"
        assert EXPECTED["address"].split(",")[0] in profile.address, (
            f"Address mismatch: {profile.address}"
        )

        # Collect URLs
        fb_urls = [
            sp.url for sp in profile.social_profiles
            if sp.platform.lower() == "facebook"
        ]
        ig_urls = [
            sp.url for sp in profile.social_profiles
            if sp.platform.lower() == "instagram"
        ]
        rappi_urls = [
            dp.get("url") for dp in profile.delivery_platforms
            if "rappi" in dp.get("name", "").lower()
        ]

        # Verify Facebook
        fb_match = any(
            normalize_url(u) == normalize_url(EXPECTED["facebook"])
            for u in fb_urls
        )
        assert fb_match, f"Facebook not found. Got: {fb_urls}"

        # Verify Instagram
        ig_match = any(
            normalize_url(u) == normalize_url(EXPECTED["instagram"])
            for u in ig_urls
        )
        assert ig_match, f"Instagram not found. Got: {ig_urls}"

        # Verify Rappi
        rappi_match = any(
            normalize_url(u) == normalize_url(EXPECTED["rappi"])
            for u in rappi_urls
        )
        assert rappi_match, f"Rappi not found. Got: {rappi_urls}"

        print("✓ test_full_enrichment PASSED")
        print(f"  Facebook:  {fb_urls}")
        print(f"  Instagram: {ig_urls}")
        print(f"  Rappi:     {rappi_urls}")
        return True
    except AssertionError as e:
        print(f"✗ test_full_enrichment FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ test_full_enrichment ERROR: {e}")
        return False
    finally:
        await svc.close()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Enrichment Social Media & Delivery Integration Tests")
    print("=" * 60)
    print()

    results = {}

    # Run individual probing tests (fast, no full enrichment)
    if "--full-only" not in sys.argv:
        print("--- Individual Probing Tests ---")
        results["facebook_probing"] = await test_facebook_probing()
        results["instagram_probing"] = await test_instagram_probing()
        results["rappi_discovery"] = await test_rappi_discovery()
        print()

    # Run full enrichment test (slower, ~2 min)
    if "--probe-only" not in sys.argv:
        print("--- Full Enrichment Test ---")
        results["full_enrichment"] = await test_full_enrichment()
        print()

    # Summary
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("ALL TESTS PASSED ✓")
        sys.exit(0)
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"FAILED: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
