"""
EditOrDeleteModule
Author: Yogesh
Objective: Search, Select and Edit or Delete a program on expanion platform.
Date:22/07/2017
Prerequisite: Python3, EasyGUI, pymysql
"""


import pymysql.cursors
import easygui

TITLE = "Expanion.com"


def search_by():
    """
    Function to ask user for type of search they want to perform and return the response,
    if response is valid, it returns tuple; False otherwise
    :return: tuple or False
    """

    # Available search options
    choices = list(enumerate(["Program ID contains"]))
                               # "Expert name contains",
                               # "Batch ID contains",
                               # "Course ID contains"]

    # Ask for Search type
    search_type = easygui.choicebox(msg="Please select the method with which you want to search.",
                                    title=TITLE,
                                    choices=choices,
                                    )
    try:
        search_type_index, search_type_str = eval(search_type)

        # Ask for search input value
        search_query = easygui.enterbox(msg="Please provide minimum 3 characters of %s" % search_type_str)

        if search_query:
            return search_type_index, search_query
        else:
            print("Invalid input for search query")
            return False

    except TypeError:
        print("No response for search type. Exiting Now!")
        return False


def query_return(resp):
    """
    Takes response from search_by() and return a dictionary holding queries and corresponding argument list,
    else False
    :param resp: search_by()
    :return: dict or False
    """
    sql_l = []
    search_type, search_query = resp
    return_dict = {'search_query': [search_query]}

    do_what = easygui.buttonbox(msg="Select an operation",
                                title=TITLE,
                                choices=["Delete", "Update"]
                                )

    if search_type == 0:
        if do_what == "Delete":
            matched_programs = sql_performer({'sqls': ["SOME_SQL_QUERY_HERE"],
                                              'search_query': [int(search_query)]}
                                             )
            if matched_programs:
                exp_id = easygui.choicebox(msg="Found following with %s in program IDs" % search_query,
                                           title=TITLE,
                                           choices=matched_programs)
            else:
                print("No result found with Program ID containing %s " % search_query)
                return False
            try:
                search_query = eval(exp_id)[0].strip()
            except ValueError:
                print("Invalid selection from matched data.")
                return False
            sql_l = ["SOME_SQL_QUERY_HERE",
                     "SOME_SQL_QUERY_HERE",
                     "SOME_SQL_QUERY_HERE"]

            # Argument for sql queries, ref to sql_performer()
            return_dict['search_query'] = [search_query]*3
            return_dict['sqls'] = sql_l
        else:
            print("Update will be available soon!")
            return False
        return return_dict
    else:
        return False


def sql_performer(input_dict):
    """
    Takes input as dictionary of sql queries' and their corresponding arguments' list,
    return list of results or status of the query
    :param input_dict: dict
    :return: list or boolean
    """
    try:
        db = pymysql.connect(host="replace_with_host_name_or_address",
                             user="replace_with_username",
                             password="replace_with_password",
                             db="replace_with_database"
                             )
        try:
            query_list = []
            update = fetch = False
            with db.cursor() as cur:
                print("Connected to the cursor")
                for sql, args in zip(input_dict['sqls'], input_dict['search_query']):
                    # zipped the args in query_return to use here, which is best practice to
                    # prevent from sql-injection
                    query_list.append(sql % args)
                    cur.execute(sql.strip(), (args,))
                    if sql.startswith('DELETE') or sql.startswith('UPDATE'):
                        update = True
                    elif sql.startswith('SELECT'):
                        fetch = True
                        result = cur.fetchall()

            if update:
                try:
                    y_n = easygui.ccbox(msg="Following changes would be made\n" +
                                            "\n".join(str(e) for e in query_list) + "\n" +
                                            "Do you want to proceed?")
                    if y_n:
                        db.commit()
                    else:
                        db.rollback()
                    print("Changed successfully made to the database!")
                    return True
                except:
                    print("Some error occured")
                    db.rollback()
                    return False

            if fetch:
                print("Got following result(s): ")
                for i in result:
                    print(i)
                return result

        except:
            print("Some error fetching data.")

    except pymysql.err.OperationalError:
        print("Access Denied")

    finally:
        db.close()


def main():
    """
    Entry Point of the program
    """
    mode = easygui.buttonbox(msg="Select the mode",
                             title=TITLE,
                             choices=["Select and Perform",
                                      "Search and Perform",
                                      "Cancel"]

                             )
    if not mode or mode == "Cancel":
        return
    elif mode == "Search and Perform":
        search_by_response = search_by()
        if search_by_response:
            sql_input_dict = query_return(search_by_response)
        else:
            return False
        if sql_input_dict:
            sql_performer(sql_input_dict)
        else:
            return False
    elif mode == "Select and Perform":
        print("Coming soon!")
    else:
        print("Invalid response")
main()
