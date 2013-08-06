import roman

# NOTE: this is NOT a production code, it is intentionally kept to the minimum
arab = int(open('arab').read())
open('roman', 'w').write(roman.toRoman(arab))
