def serialize_post1(post, post_id):
    resp = {
        'date': post[0].isoformat(sep=' '),
        'dislikes': post[11],
        'forum': post[4],
        'id': post_id,
        'isApproved': bool(post[6]),
        'isDeleted': bool(post[10]),
        'isEdited': bool(post[8]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[9]),
        'likes': post[12],
        'message': post[2],
        'parent': post[5],
        'points': post[13],
        'thread': post[1],
        'user': post[3]
    }
    return resp


def posts_to_list(posts):
    resp = []
    for post in posts:
        resp.append(serialize_post1(post[1:], post[0]))
    print(resp)
    return resp