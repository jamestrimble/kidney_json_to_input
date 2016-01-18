echo "This script performs diffs of expected and actual output."
echo "If there is no output after this line, the test pass."
diff test-fixtures/1.input_and_ndds <(python kjti/kjti.py test-fixtures/1.json)
diff test-fixtures/1.input_and_ndds <(python kjti/kjti.py test-fixtures/1a.json)
diff test-fixtures/2.input_and_ndds <(python kjti/kjti.py test-fixtures/2.json)
