import instaloader

ALLOWED_ACCOUNTS = {"pao.arandaok", "costapalomashowroom"}


def normalize_username(value: str) -> str:
    return value.strip().lstrip("@").lower()


def get_profile_data(username: str) -> dict:
    username = normalize_username(username)
    if username not in ALLOWED_ACCOUNTS:
        raise ValueError("Cuenta no permitida")

    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    profile = instaloader.Profile.from_username(loader.context, username)

    posts = []
    if not profile.is_private:
        try:
            for i, post in enumerate(profile.get_posts()):
                if i >= 8:
                    break
                posts.append({
                    "shortcode": post.shortcode,
                    "date": post.date_utc.isoformat() + "Z",
                    "is_video": post.is_video,
                    "likes": post.likes,
                    "comments": post.comments,
                    "caption": (post.caption or "")[:500],
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                })
        except instaloader.exceptions.ConnectionException:
            pass

    return {
        "username": profile.username,
        "full_name": profile.full_name,
        "is_private": profile.is_private,
        "is_verified": profile.is_verified,
        "biography": profile.biography,
        "external_url": profile.external_url,
        "followers": profile.followers,
        "followees": profile.followees,
        "mediacount": profile.mediacount,
        "profile_pic_url": str(profile.profile_pic_url),
        "posts": posts,
    }
