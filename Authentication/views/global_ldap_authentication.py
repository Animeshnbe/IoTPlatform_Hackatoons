from ldap3 import Server, Connection, ALL, SUBTREE,SAFE_SYNC, SIMPLE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import ssl
from ldap3.core.tls import Tls


def global_ldap_authentication(user_name, user_pwd):
    """
      Function: global_ldap_authentication
       Purpose: Make a connection to encrypted LDAP server.
       :params: ** Mandatory Positional Parameters
                1. user_name - LDAP user Name
                2. user_pwd - LDAP User Password
       :return: None
    """

    # fetch the username and password
    ldap_user_name = user_name.strip()
    ldap_user_pwd = user_pwd.strip()
    # tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
    # ldap server hostname and port
    ldsp_server = f"ldap://localhost:389"

    # dn
    root_dn = "dc=example,dc=org"

    # user
    user = f'cn={ldap_user_name},{root_dn}'
    
    print("LDAP USER == ",user)
    server = Server(ldsp_server,get_info=ALL)
    print(f" *** Server \n{server}" )
    connection = Connection(server,
                            user=user,
                            password=ldap_user_pwd,
                            )
    print(f" *** Response from the ldap bind is \n{connection}" )
    if not connection.bind():
        print(f" *** Cannot bind to ldap server: {connection.last_error} ")
        l_success_msg = f' ** Failed Authentication: {connection.last_error}'
    else:
        print(f" *** Successful bind to ldap server")
        l_success_msg = 'Success'

    return l_success_msg