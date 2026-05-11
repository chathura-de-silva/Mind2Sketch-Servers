```markdown

```

# MinIO — Install and Run

Step-by-step instructions to download, install, and run MinIO on a Linux host using wget.

1. Create a directory for MinIO and data (optional):

	mkdir -p ~/minio-bin ~/minio-data

2. Download the MinIO server binary with wget:

	cd ~/minio-bin
	wget https://dl.min.io/server/minio/release/linux-amd64/minio -O minio

3. Make the binary executable:

	chmod +x minio

4. Run MinIO (replace "whatever" with your desired access key and secret key):

	cd ~
	MINIO_ROOT_USER=`"whatever"` MINIO_ROOT_PASSWORD=`"whatever"` \
	~/minio-bin/minio server ~/minio-data --console-address ":9001"

	- MINIO_ROOT_USER and MINIO_ROOT_PASSWORD: set your access key and secret key.
	- ~/minio-data: directory where object data will be stored.
	- --console-address ":9001": web admin console port.


Notes:
 - For production, choose strong credentials and consider running MinIO as a systemd service, behind TLS and a firewall.
 - Change paths and ports as needed.

