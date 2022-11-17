import hashlib

def hex_md5(text):
	return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()


if __name__ == '__main__':
	print(hex_md5('test'))