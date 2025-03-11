ID=$(curl -H "Authorization: Bearer $API_TOKEN" \
       -F "ProjectSlug=$PROJECT" \
       -F "SigningPolicySlug=ChemDoE_TEST" \
       -F "ArtifactConfigurationSlug=v0.1.1" \
       -F "Artifact=@./dist/ChemDoE.exe" \
       -F "Description=A Chemotion DoE tool" \
       https://app.signpath.io/API/v1/$ORGANIZATION_ID/SigningRequests | jq -r '.signingRequestId')


curl -H "Authorization: Bearer " \
     -o ./dist/ChemDoE_s.exe \
     https://app.signpath.io/API/v1/$ORGANIZATION_ID/SigningRequests/$ID/SignedArtifact