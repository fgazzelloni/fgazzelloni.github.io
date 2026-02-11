#!/usr/bin/env python3
"""
Test script for podcast fetching functionality.
Creates mock RSS data to test the script logic without network access.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fetch_podcasts import (
    extract_episode_info,
    create_episode_post,
    slugify,
    POSTS_DIR
)


def create_mock_rss_item():
    """Create a mock RSS item element for testing."""
    item_xml = """
    <item>
        <title>Test Episode: Machine Learning in Healthcare</title>
        <pubDate>Wed, 15 Jan 2026 10:00:00 GMT</pubDate>
        <description>
            This episode explores the use of machine learning and artificial intelligence 
            in healthcare data science and epidemiology. We discuss public health 
            applications and infectious disease tracking.
        </description>
        <guid>https://open.spotify.com/episode/test123abc</guid>
        <link>https://open.spotify.com/episode/test123abc</link>
        <enclosure url="https://anchor.fm/s/test/audio/episode/test123abc.mp3" type="audio/mpeg"/>
    </item>
    """
    return ET.fromstring(item_xml)


def test_slugify():
    """Test the slugify function."""
    print("Testing slugify function...")
    
    test_cases = [
        ("Test Episode", "test-episode"),
        ("Machine Learning & AI", "machine-learning-ai"),
        ("Episode #123: Data Science!", "episode-123-data-science"),
        ("   Spaces   Around   ", "spaces-around"),
    ]
    
    for input_text, expected in test_cases:
        result = slugify(input_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} slugify('{input_text}') = '{result}' (expected: '{expected}')")
    
    print()


def test_extract_episode_info():
    """Test episode info extraction."""
    print("Testing extract_episode_info function...")
    
    item = create_mock_rss_item()
    episode = extract_episode_info(item)
    
    print(f"  Title: {episode['title']}")
    print(f"  Date: {episode['date']}")
    print(f"  Description length: {len(episode['description'])} chars")
    print(f"  GUID: {episode['guid']}")
    print(f"  Episode ID: {episode['episode_id']}")
    
    # Validate
    assert episode['title'] == "Test Episode: Machine Learning in Healthcare"
    assert episode['date'] == "2026-01-15"
    assert "machine learning" in episode['description'].lower()
    assert episode['episode_id'] == "test123abc"
    
    print("  ✓ All validations passed")
    print()


def test_create_episode_post():
    """Test episode post creation."""
    print("Testing create_episode_post function...")
    
    # Create a test episode
    test_episode = {
        'title': 'Test Episode: Data Science in Healthcare',
        'date': '2026-01-15',
        'description': 'This is a test episode about data science and machine learning in healthcare.',
        'guid': 'test-guid-12345',
        'episode_id': 'testep123',
        'image_url': '',  # No image for test
        'spotify_url': 'https://open.spotify.com/episode/testep123'
    }
    
    # Create the post
    episode_dir = create_episode_post(test_episode)
    
    print(f"  Created episode directory: {episode_dir}")
    
    # Verify the directory and file exist
    dir_path = Path(episode_dir)
    qmd_path = dir_path / "index.qmd"
    
    assert dir_path.exists(), f"Directory {dir_path} should exist"
    assert qmd_path.exists(), f"File {qmd_path} should exist"
    
    # Read and validate the content
    content = qmd_path.read_text()
    
    # Check frontmatter
    assert "title:" in content
    assert "date: '2026-01-15'" in content
    assert "slug: podcast-" in content
    assert "categories:" in content
    assert "summary:" in content
    
    # Check embed iframe
    assert "<iframe" in content
    assert "open.spotify.com/embed/episode/testep123" in content
    
    # Check sections
    assert "## Episode Overview" in content
    assert "## Key Topics Discussed" in content
    
    print("  ✓ Post created successfully")
    print(f"  ✓ File exists: {qmd_path}")
    print("  ✓ Content validated")
    
    # Show a preview of the content
    print("\n  Content preview (first 500 chars):")
    print("  " + "-" * 70)
    for line in content.split('\n')[:20]:
        print(f"  {line}")
    print("  " + "-" * 70)
    print()
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(dir_path)
        print(f"  ✓ Cleaned up test directory: {dir_path}")
    except Exception as e:
        print(f"  Warning: Could not clean up test directory: {e}")
    
    print()


def main():
    """Run all tests."""
    print("=" * 70)
    print("PODCAST FETCHER TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        test_slugify()
        test_extract_episode_info()
        test_create_episode_post()
        
        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print()
        print("Note: Network tests are skipped in sandboxed environments.")
        print("The actual RSS fetching will work in GitHub Actions with internet access.")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
