# Working with Data - CLI Tools

##### jq

##### Request the JSON users content from the previous example and pass it to `jq`


```bash
curl -s 'https://jsonplaceholder.typicode.com/users' | jq .
```

##### Read the `basic_example.json` file


```bash
jq . basic_example.json
```

##### Another way to read in the `basic_example.json` file


```bash
cat basic_example.json | jq
```

##### Return all items of the list 


```bash
jq '.[]' basic_example.json
```

##### Return the first item or index 0 from the list


```bash
jq '.[0]' basic_example.json
```

##### Get the value of a key called `name` in the first list item


```bash
jq '.[0].name' basic_example.json
```

##### Get all names from the list


```bash
jq '.[].name' basic_example.json
```

##### Print the values of the `id` and `name` keys


```bash
jq '.[] | {id, name}' basic_example.json
```

##### Join the IDs and Names in the format `id - name`


```bash
jq  '.[] | {id, name} | join (" - ")' basic_example.json
```

##### Remove the quotes


```bash
jq --help | grep raw
echo
jq -r '.[] | {id, name} | join (" - ")' basic_example.json
```

##### Only return items which match a criteria


```bash
jq '.[] | select((.name == "Ervin Howell") or ( .name | contains("Leanne")))' basic_example.json
```

##### Only return items which match a criteria and then only print the value of the `address` key in that item


```bash
jq '.[] | select(.name == "Ervin Howell") | {address}' basic_example.json
```

##### Only return items which match a criteria and then only print all keys foudn in `address` 


```bash
jq '.[] | select(.name == "Ervin Howell") | {address} | .address | keys '  basic_example.json
```

##### Only return items which match a criteria and then print the value of a specific key in that item


```bash
jq '.[] | select(.name == "Ervin Howell") | {address} | .address.city ' basic_example.json
```

##### Show the JSON for a new user


```bash
cat new_user.json
```

##### Append it as an item to the list in `basic_example.json`


```bash
jq '. += [input]' basic_example.json new_user.json
```

##### Notice that `basic_example.json` does not contain the new user?


```bash
cat basic_example.json
```

##### Write the new appended list to a temporary file and print the contents


```bash
jq '. += [input]' basic_example.json new_user.json > temp_list_of_users.json
cat temp_list_of_users.json
```

##### Use this temporary file in a shell script


```bash
echo -e "Using jq in a shell script \n"

list_of_names=$(jq -r '.[].name | @sh' temp_list_of_users.json)

for i in "${list_of_names[@]}"; do
    echo "$i"
done

```

"The `@foo` syntax is used to format and escape strings, which is useful for building URLs, documents in a language like HTML or XML, and so forth."

"`@sh`:
The input is escaped suitable for use in a command-line for a POSIX shell. If the input is an array, the output will be a series of space-separated strings."

https://devdocs.io/jq/

"`@`	Used in filter expressions to refer to the current node being processed."

https://support.smartbear.com/alertsite/docs/monitors/api/endpoint/jsonpath.html


##### Remove the temporary file


```bash
rm temp_list_of_users.json
```
