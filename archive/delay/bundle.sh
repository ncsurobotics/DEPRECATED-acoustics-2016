#!/bin/sh

LIBSEAWOLF_INSTALL=${LIBSEAWOLF_INSTALL:-~/libseawolf/src}
SERVER_IP=${SERVER_IP:-192.168.1.85}

# Ensure build is up to date
make

if [ -d acoustics ]; then
    echo "The acoustics directory already exists. I need that as a temporary directory";
    exit 1;
fi

echo -n "Generating bundle...";

# Build directory structure
mkdir acoustics;
mkdir acoustics/filters;
mkdir acoustics/lib;

# Copy binaries
cp bin/acoustics-bfin ../driver/ppiadc.ko acoustics;
cp ${LIBSEAWOLF_INSTALL}/libseawolf.so* acoustics/lib;

# Generate config files and scripts
cat <<EOF > acoustics/seawolf.conf
comm_server = ${SERVER_IP}
comm_password = 
EOF

cat <<EOF > acoustics/update
#!/bin/sh
cd /root
tftp -g -r acoustics.tar ${SERVER_IP}
tar -xf acoustics.tar && rm acoustics.tar
cd acoustics
./init
EOF

cat <<EOF > acoustics/init
#!/bin/sh
cp /root/acoustics/lib/* /usr/lib
if cat /proc/modules | grep ppiadc > /dev/null 2>&1; then
    rmmod ppiadc
fi
insmod /root/acoustics/ppiadc.ko
mknod /dev/ppiadc c 157 0
EOF

cat <<EOF > acoustics/export_dump
#!/bin/sh
for f in dump_*; do
    tftp -p -l \$f ${SERVER_IP}
done
EOF

chmod +x acoustics/update acoustics/init acoustics/export_dump;

# Build FIR coefficient files
for f in ../filters/*.fcf; do
    python ../filters/convert.py < $f > acoustics/filters/`basename $f .fcf`.cof;
done;

tar -cf acoustics.tar acoustics;
rm -rf acoustics;

echo "done.";
