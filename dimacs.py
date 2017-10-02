class DimacsMapper(object):
    def __init__(self, mapper):
        self.mapper = mapper

    def value(self, name):
        """
        Method to convert a given variable name (e.g. 1_2__0) into 
        its index.  
        """
        return -(self.mapper.index(name[1:]) + 1) if name[0] == '-' else self.mapper.index(name) + 1

    def name(self, value):
        """
        Get the inverse (original name and not-whatever status)
        """
        return "%s%s" % ("" if value > 0 else "-", self.mapper.name(abs(value) - 1))

    def encode(self, cnf):
        # we construct the cnf
        cnf_raw = [[self.value(variable) for variable in clause] for clause in cnf]

        # the header that is required
        header = "p cnf %d %d\n" % (self.mapper.size(), len(cnf))
        
        # now we can finally return the raw dimacs
        return header + "\n".join([" ".join([str(el) for el in clause]) + " 0" for clause in cnf_raw])

    def size(self):
        return self.mapper.size()
