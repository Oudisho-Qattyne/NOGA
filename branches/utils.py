import math

def haversine(coord1, coord2):
    # إحداثيات على شكل (lat, lon)
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # نصف قطر الأرض بالكيلومترات

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # المسافة بالكيلومترات

def parse_location(loc_str):
    print(loc_str)
    lat_str, lon_str = loc_str.split(',')
    return float(lat_str), float(lon_str)

def nearest_branch(user_location, branches):
    user_coord = parse_location(user_location)
    min_distance = float('inf')
    nearest = None
    for branch in branches:
        branch_coord = parse_location(branch)
        dist = haversine(user_coord, branch_coord)
        if dist < min_distance:
            min_distance = dist
            nearest = branch
    return nearest, min_distance
