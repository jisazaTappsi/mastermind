#!/usr/bin/env python

"""Defines a more user friendly way of entering data."""

import warnings

from boolean_solver.constants import *
from boolean_solver.output import Output
from boolean_solver.util import helpers
from boolean_solver.util.last_update_dict import LastUpdateDict
from boolean_solver.util.last_update_set import LastUpdateSet
from boolean_solver.util.code_dict import CodeDict

__author__ = 'juan pablo isaza'


class Conditions(list):
    """
    It is a list that contains conditions, each being a dictionary with the inputs.
    """

    @staticmethod
    def gets_start_positional_idx(dictionary):
        """
        Gets the biggest index for a dictionary and add 1.
        :param dictionary: any dict
        :return: int
        """
        max_idx = 0
        has_key = False
        for key in dictionary:
            if isinstance(key, str) and re.match("^" + POSITIONAL_ARGS_RULE + "\d+$", key) is not None:
                has_key = True
                r = re.search("\d+$", key)
                candidate = int(r.group())
                if candidate > max_idx:
                    max_idx = candidate

        if has_key:
            return max_idx + 1
        else:
            return 0

    def get_max_positional_arg(self):
        """
        Gets the index for the next positional argument to start.
        :return: int.
        """
        max_arg = 0
        for d in self:
            candidate = self.gets_start_positional_idx(d)
            if candidate > max_arg:
                max_arg = candidate

        return max_arg

    def search_repeating_variable(self, value):
        """Tries to find if variable was already declared. If so outputs the original key else outputs None. Will
        exclude reserved words, as they are not variable declarations.
        :param value: a variable value. For example a Code object.
        :return : key of possible repeating variable  or None
        """
        for d in self:
            for key in set(d.keys()) - set(KEYWORDS.values()):
                if d[key] == value:
                    return key
        return None

    def get_ordered_dict(self, args, kwargs):
        """
        Big issue solved here. Adds args, to have positional args always in the same order as the user inputs.
        Therefore the user can have short circuiting for logical operators, by having inputs in the right order.
        :param args: positional args. Used when specific order required.
        :param kwargs: a common dict
        :return: the right dict for the job a LastUpdatedOrderedDict.
        """
        ordered_dict = LastUpdateDict()

        # Adds args
        start_idx = self.get_max_positional_arg()
        for idx, e in enumerate(args):

            repeating_var = self.search_repeating_variable(e)
            if repeating_var is None:  # first time: declares new value.
                ordered_dict[POSITIONAL_ARGS_RULE + str(start_idx + idx)] = e
            else:  # has been previously declared.
                ordered_dict[repeating_var] = e

        # Adds kwargs
        for k in kwargs.keys():
            ordered_dict[k] = kwargs[k]

        return ordered_dict

    def __init__(self, *args, **kwargs):
        """
        init and add new parameters if provided.
        :param kwargs:
        :return:
        """
        list.__init__(list())

        if len(kwargs) > 0:
            self.append(self.get_ordered_dict(args, kwargs))

    def add(self, *args, **kwargs):
        """
        Adds a new row condition.
        :param kwargs: dictionary like parameters.
        :return: void
        """
        if len(kwargs) > 0:
            self.append(self.get_ordered_dict(args, kwargs))
        else:
            warnings.warn('To add condition at least 1 argument should be provided', UserWarning)

    def get_input_values(self, f_inputs, output):
        """
        Scans the whole conditions object looking for input values, adds them with the function inputs.
        :param f_inputs: function inputs.
        :param output: the output of the row.
        :return: All possible inputs that are not keywords.
        """
        remove_elements = KEYWORDS.values()

        f_inputs = list(f_inputs)
        input_values = []
        for row in self:
            if KEYWORDS[OUTPUT] in row and row[KEYWORDS[OUTPUT]] == output:
                keys = helpers.remove_list_from_list(row.keys(), f_inputs)
                keys = helpers.remove_list_from_list(keys, remove_elements)
                input_values += [row[k] for k in keys]

        return f_inputs + input_values

    def get_input_keys(self, f_inputs, output):
        """
        Scans the whole conditions object looking for input keys. Will add inputs (such as code pieces), that are not
        explicitly declared as function inputs.
        Uses LastOrderSets because order is very important. The order is:
        first the f_inputs (ordered from right to left), then args added on the condition object from right to left and
        top to bottom.
        Example:
        >>>out = -1

        >>>def f(a, b):
        >>>    return a + b

        >>>cond = Conditions(c=1, d=2, output=out)
        >>>cond.add(x=3, y=4, output='other_stuff')
        >>>cond.add(e=3, f=4, output=out)

        >>>cond.get_input_keys(helpers.get_function_inputs(f), out)
        >>>LastUpdateSet(['a', 'b', 'c', 'd', 'e', 'f'])

        :param f_inputs: function inputs.
        :param output: the output of the row.
        :return: All possible inputs that are not keywords.
        """
        # TODO: missing optional args(kwargs) of the input function.
        f_inputs = LastUpdateSet(f_inputs)
        new_inputs = LastUpdateSet()

        for row in self:
            if KEYWORDS[OUTPUT] in row and row[KEYWORDS[OUTPUT]] == output:
                new_inputs |= LastUpdateSet(row.keys()) - f_inputs  # adds inputs who are not already args.

        all_elements = f_inputs | new_inputs

        return all_elements - KEYWORDS.values()

    @staticmethod
    def add_element_to_tuples(tuples_set, new_element):
        """
        Adds additional element to a tuple set.
        :param tuples_set: a set containing tuples.
        :param new_element: any element to add in last position.
        :return: tuple set
        """
        new_tuples = LastUpdateSet()
        for tuple_element in tuples_set:
            new_tuples.add(tuple_element + (new_element,))

        return new_tuples

    def get_tuples_from_args(self, row, function_args, output):
        """
        Get a set containing tuples (with implicit or explicit rows).
        :param row: dict with index as key and value as input value.
        :param function_args: function
        :param output: the output of the row.
        :return: set containing tuples.
        """

        if helpers.var_is_false(output):
            return LastUpdateSet()

        # starts with 1 tuple
        tuples = LastUpdateSet([()])
        for variable in self.get_input_keys(function_args, output):

            if variable in row:
                tuples = self.add_element_to_tuples(tuples, row[variable])
            else:

                # All possible outcomes for undetermined boolean variable: duplicates number of tuples.
                true_tuples = self.add_element_to_tuples(tuples, True)
                false_tuples = self.add_element_to_tuples(tuples, False)
                tuples = true_tuples | false_tuples

        # add explicit output to tuples, if necessary.
        return tuples

    @staticmethod
    def is_explicit(row):
        """
        Does the output is explicitly named on this table row. Has 2 elements the first is tuple.
        :param row: table row, or a condition.
        :return: boolean
        """
        return len(row) == 2 and isinstance(row[0], tuple)

    @staticmethod
    def get_output(row):
        """
        Gets the output from a row.
        :param row: dict.
        :return: output function or output or True if not specified.
        """
        out_key = KEYWORDS[OUTPUT]
        args_key = KEYWORDS[OUTPUT_ARGS]
        if out_key in row and args_key in row:  # This case is encountered only when the output is a function.
            return Output(function=row[out_key], arguments=row[args_key])
        elif out_key in row:
            return row[out_key]

        return True

    @staticmethod
    def row_has_non_keyword_keys(row):
        """
        Boolean output indicating whether a row (dict) has non keyword keys.
        :param row: dict.
        :return: True if there is at least 1 input different from a keyword.
        """
        row_keys = set(row.keys())
        keyword_keys = set(KEYWORDS.values())
        return len(row_keys.difference(keyword_keys)) > 0

    @staticmethod
    def change_key_from_bool_to_int(d, new_key):
        """
        Changes the keys from booleans (True or False) to int(0 or 1)
        if a int(0 or 1) is present.
        :param d: dict
        :param new_key: a new key to be added to dict.
        :return: new dict
        """
        if helpers.var_is_1(new_key) and helpers.has_true_key(d):
            d[1] = d.pop(True, None)

        if helpers.var_is_0(new_key) and helpers.has_false_key(d):
            d[0] = d.pop(False, None)

        return d

    def add_truth_table(self, truth_tables, row, function_args):
        """
        Adds a new truth table to the dict of truth_tables.
        :param truth_tables: orderDict, where the key is the output and the inputs are a orderSet of values.
        :param row: 1 row of self.
        :param function_args: tuple
        :return: modified truth_tables.
        """
        output = self.get_output(row)

        if output in truth_tables:  # uses existing table.
            truth_table = truth_tables[output]
        else:  # adds new truth table
            truth_table = LastUpdateSet()

        condition_rows = self.get_tuples_from_args(row, function_args, output)
        truth_table = truth_table | condition_rows  # concat sets.

        truth_tables[output] = truth_table  # add to tables dict.

        return self.change_key_from_bool_to_int(truth_tables, output)

    def get_truth_tables(self, function_args):
        """
        Factor Truth tables by output.
        This is the 'private' version.
        :param function_args: variables.
        :return: CodeDict(), where key=output and value=implicit truth table.
        """

        # dict where outputs are the keys, values are the rows.
        truth_tables = CodeDict()

        for row in self:
            if self.row_has_non_keyword_keys(row):
                truth_tables = self.add_truth_table(truth_tables, row, function_args)

        return truth_tables


def add_to_dict_table(table, key, value):
    """
    Converts the table from tuples (explicit or implicit) to a dict().
    Where the key is the output.
    :param table: dict
    :param key: to be added to dict
    :param value: to be added to dict
    :return: modified table
    """
    # will ignore key=False
    if key:
        if key in table:  # add value to set in already existing key value pair.
            table[key] = table[key] | LastUpdateSet([value])
        else:  # create new key value pair.
            table[key] = LastUpdateSet([value])

    return table


def from_raw_set_to_dict_table(conditions):
    """
    Convert raw case to general format.
    :param conditions: obj
    :return: dict where key is output and value is implicit truth table.
    """
    table = dict()
    for row in conditions:
        if Conditions.is_explicit(row):  # explicit case
            table = add_to_dict_table(table, row[1], row[0])
        else:  # implicit case
            table = add_to_dict_table(table, True, row)

    return table

TYPE_ERROR = 'type_error'
ROW_ERROR = 'row_error'
EXPLICIT_ROW_ERROR = 'explicit_row_error'


class ConditionsTypeError(TypeError):
    def __init__(self, error_object, error_type):
        if TYPE_ERROR == error_type:
            message = 'Conditions variable is not a set nor a Conditions object, but rather type {}'\
                .format(type(error_object))
        elif ROW_ERROR:
            message = '{} row in truth table is not a tuple'.format(error_object)
        elif EXPLICIT_ROW_ERROR:
            message = '{} row with explicit output in truth table has wrong format.'.format(error_object)
        else:
            message = 'unknown TypeError'

        super(ConditionsTypeError, self).__init__(message)


def get_truth_tables(conditions, function_args):
    """
    This is the 'public' version of the class method with the same name.
    :param conditions: either a truth table or a conditions object.
    :return: truth table (ie set with tuples).
    """
    if isinstance(conditions, Conditions):
        return conditions.get_truth_tables(function_args)
    elif isinstance(conditions, set) or isinstance(conditions, LastUpdateSet):  # raw set case.
        return from_raw_set_to_dict_table(conditions)
    else:
        raise ConditionsTypeError(conditions, TYPE_ERROR)


def valid_conditions(conditions):
    """
    Valid conditions must be sets, LastUpdateSet, inherit from set or be a Conditions object.
    - set case:  When the input is a raw table. If conditions is a set then all rows have to be tuples or inherit
    from tuple.
    - LastUpdateSet case: same as set.
    - Conditions case: When the input is a Conditions object.
    :param conditions: truth table or a conditions object.
    :return: boolean.
    """
    if not isinstance(conditions, set)\
            and not isinstance(conditions, Conditions)\
            and not isinstance(conditions, LastUpdateSet):
        raise ConditionsTypeError(conditions, TYPE_ERROR)

    # only for set and LastUpdateSet.
    if isinstance(conditions, set) or isinstance(conditions, LastUpdateSet):
        for row in conditions:
            if not isinstance(row, tuple):
                raise ConditionsTypeError(row, ROW_ERROR)

            # when the output is explicit, check for 2 elements of outer tuple.
            if isinstance(row[0], tuple):
                if len(row) != 2:
                    raise ConditionsTypeError(row, EXPLICIT_ROW_ERROR)

    return True
