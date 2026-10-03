# See disks
lsblk

# See filesystem/UUID information
lsblk -f

# Create mount point
sudo mkdir /mnt/recovery

# Mount snapshot recovery filesystem
sudo mount -o nouuid /dev/nvme1n1p1 /mnt/recovery

# Verify mount
mount | grep /mnt/recovery

# Look inside recovered filesystem
ls -la /mnt/recovery

# Find backup data
sudo find /mnt/recovery -name "backup-data" -type d 2>/dev/null

# Check recovered files
ls -la /mnt/recovery/home/ec2-user/backup-data

# Unmount recovery volume
sudo umount /mnt/recovery

# Check disks again
lsblk