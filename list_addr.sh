#!/bin/bash -e

dir_addr="addr_csv/"

base_file="${dir_addr}addr_list.eth.csv"
echo "address" >"$base_file"

for file in ${dir_addr}out?.eth.csv; do
    echo "$file"
    if [ -f "$file" ]; then
        tail -n +2 "$file" >>"$base_file"
    fi
done

echo "Done $(wc -l <"$base_file")"
