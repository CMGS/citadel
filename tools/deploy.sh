#!/bin/sh


set -e
deploy_mode=${1-test}
remote=${2-origin}
branch=${3-master}

if [ $deploy_mode == "test" ]
then
  ssh c1-eru-2 << EOF
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git fetch --all --prune
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git reset --hard $remote/$branch
  sudo systemctl restart citadel citadel-worker watch-etcd
EOF
elif [ $deploy_mode == "prod" ]
then
  cat > ~/.corecli.json << EOF
{"sso_url": "http://sso.ricebook.net", "citadel_url": "http://citadel.ricebook.net", "auth_token": "nHBKNpFBbRe5nRbuS2Z1ta7IkDQpcie0i4qRf09W5oBeWl5PcktCOykhBbT8vtDQ", "mimiron_url": "", "username": "liuyifu"}
EOF
  echo "corecli config has been set to citadel.ricebook.net"
  ssh c2-eru-1 << EOF
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git fetch --all --prune
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git reset --hard $remote/$branch
  sudo systemctl restart citadel citadel-worker watch-etcd

EOF
  # update zone c1 watch-etcd.service
  ssh c1-eru-1 << EOF
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git fetch --all --prune
  sudo git --work-tree=/opt/citadel --git-dir=/opt/citadel/.git reset --hard $remote/$branch
  sudo systemctl restart watch-etcd
EOF
else
  exit 127
fi
