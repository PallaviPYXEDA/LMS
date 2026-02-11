export const awsIdentityConfig = {
    Auth: {
        Cognito: {
            identityPoolId: 'us-east-1:13a0d10e-c5b2-40f7-b68c-cc2e996db798',
            region: 'us-east-1',
            userPoolClientId: '7qu83ed86c08gnk3s1285aarcn',
            userPoolId: 'us-east-1_lv776GRgS',
            loginWith: {
                oauth: {
                    domain: 'pyxeda.auth.us-east-1.amazoncognito.com',
                    scopes: ['phone', 'email', 'profile', 'openid', 'name'],
                    redirectSignIn: [""],
                    redirectSignOut: [""],
                    responseType: 'code' as const,
                }
            },
        },
    }
};
